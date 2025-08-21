### Documentação de decisões de arquitetura e implementação

#### Objetivo
O objetivo desse projeto é construir uma API para coleta de mensagens Pix com suporte a alto volume, leitura concorrente por “coletores” via stream, long polling e inserção de mensagens para testes.

### Stack e estrutura do projeto

- **Framework**: Django 5 + Django REST Framework (renderização JSON)
- **Banco**: PostgreSQL
- **Containerização**: Docker + docker-compose
- **Estrutura de apps**
  - `data`: modelos de domínio e serializers
  - `api`: rotas de stream Pix (leitura/continuação/encerramento)
  - `util`: rotas utilitárias para semear mensagens e utilidades compartilhadas
  - `health`: rota de health check, primeira funcionalidade a ser implementada para garantir que o serviço estava operando
- **Arquivos relevantes**
  - `app/data/models.py`: `PixStream`, `PixMessage`
  - `app/data/serializers.py`: `PixMessageSerializer`
  - `app/api/views.py`: `stream_start`
  - `app/util/views.py`: `generate_messages`
  - `app/util/utils.py`: utilidades para stream (long polling, reservas, consumo)
  - `app/beeteller/urls.py`: roteamento principal
  - `docker-compose.yml`, `Dockerfile`, `requirements.txt`
  - `Makefile`: importante durante o processo de desenvolvimento para o processo de build, pois estava recebendo um problema de rede devido a interação Windows + WSL

Decisão: separar domínio (`data`) das rotas (`api`) e utilidades (`util`) para melhorar coesão e facilitar testes e manutenibilidade.

### Modelagem dos dados

- `PixMessage`
  - Campos mapeiam 1:1 com a especificação:
    - Identificadores/valores: `end_to_end_id` (único), `tx_id`, `amount` (Decimal), `payment_at`
    - Pagador: `payer_*`
    - Recebedor: `receiver_*` (com `receiver_ispb` indexado para filtragem)
    - Texto livre: `free_text` (mapeado para `campoLivre` via serializer)
  - Controle de consumo: `status` em `{pending, reserved, consumed}`, `reserved_by` (FK para `PixStream`), `reserved_at`, `consumed_at`
  - Índices:
    - `receiver_ispb + status + id` para varredura ordenada por id e filtragem por ispb/status
    - `status + created_at` para inspeções e manutenção
- `PixStream`
  - `interation_id` (token opaco do stream), `ispb`, `active`, `started_at`, `last_pull_at`, `terminated_at`
  - Índice `ispb + active` para aplicação de limite de concorrência e listagens

Decisão: usar `status` + `reserved_by` para garantir que mensagens não sejam repetidas entre streams e chamadas. Essa abordagem funciona bem com `SELECT … FOR UPDATE SKIP LOCKED` em PostgreSQL.

### Serialização

- `PixMessageSerializer` em `data/serializers.py`
  - Converte:
    - `end_to_end_id` → `endToEndId`
    - `amount` → `valor`
    - `free_text` → `campoLivre`
    - `tx_id` → `txId`
    - `payment_at` → `dataHoraPagamento`
  - Constrói `pagador` e `recebedor` a partir dos campos `payer_*` e `receiver_*`

Decisão: manter nomes "Pythonic" nos modelos e fazer o mapeamento no serializer para ficar de acordo com a especificação da API.

### Endpoints implementados

- Leitura via stream (API principal):
  - GET ` /api/pix/{ispb}/stream/start`
    - Cria um `PixStream` (gera `interation_id`) se limite de 6 ativos por ISPB não for excedido
    - Realiza long polling (até 8s), reservando 1 ou até 10 mensagens conforme o `Accept`
    - Resposta:
      - 200 com mensagem única (`application/json`) ou lista (`multipart/json`)
      - 204 quando não há mensagens no período; sempre retorna `Pull-Next`
  - GET ` /api/pix/{ispb}/stream/{interationId}`
    - Continua a leitura do mesmo stream, mesma lógica de long polling e reservas
  - DELETE ` /api/pix/{ispb}/stream/{interationId}`
    - Confirma consumo: marca as mensagens `reserved` como `consumed` e encerra o stream

- Utilitários:
  - POST ` /api/util/msgs/{ispb}/{number}` (conforme estado atual das rotas, veja nota abaixo)
    - Insere `number` mensagens aleatórias, com `receiver_ispb = {ispb}`

- Health:
  - GET ` /api/health` (simples verificação do serviço)

Decisões importantes:
- **Accept header**: 
  - `application/json` → 1 mensagem por resposta
  - `multipart/json` → até 10 mensagens
- **Pull-Next**: sempre presente, apontando para o próximo GET/DELETE com o mesmo `interationId`
- **HTTP 204**: retornado após tentativa de long polling sem mensagem; `Pull-Next` continua válido
- **Concorrência**:
  - Limite de 6 `PixStream` ativos por ISPB
  - Seleção de mensagens com `SELECT … FOR UPDATE SKIP LOCKED` (via `select_for_update(skip_locked=True)`): evita competição e interleaving de mensagens entre streams concorrentes
  - Mensagens reservadas não aparecem em outro stream

### Long polling e concorrência

- Implementado em `util/utils.py`:
  - Marca `last_pull_at` no `PixStream`
  - Tenta reservar mensagens PENDING por janela de até 8s, com pequenos sleeps (200ms)
  - Usa `mark_reserved(stream)` com `status=reserved` e `reserved_by=stream`
  - Em DELETE, `consume_and_close_stream(stream)` para confirmar consumo e encerrar

Decisão: encapsular utilidades do stream em `util/utils.py` para que `api/views.py` fique leve e focado nas rotas.

### Iteration/Interation ID

- Token opaco (`interation_id`) armazenado em `PixStream`
- Gerado como string randômica
- Usado para continuar e encerrar o stream; não é ID de mensagem

Nota: O termo original da especificação usa “interationId”; mantive `interation_id` para seguir o contrato das rotas.

### Configuração e segurança

- `ALLOWED_HOSTS` configurável via `.env`; padrão inclui `0.0.0.0, localhost, 127.0.0.1`
- `CSRF`: desabilitei CSRF apenas nos endpoints utilitários e no DELETE do stream para permitir testes via curl/Postman sem sessão
  - Em produção, reavaliar exposição (autenticação e/ou escopo restrito)
- `TIMEZONE`:
  - Para timestamps de banco: `django.utils.timezone.now()` (nameado como `dj_timezone` nas utils)
  - Para gerar `endToEndId`: `datetime.now(dt_timezone.utc)` para garantir UTC consistente

### Docker e execução

- `Dockerfile`: Python 3.11 slim, instala deps, copia `app/`, expõe 8000, roda `runserver`
- `docker-compose.yml`:
  - `web` (Django) depende de `db` (Postgres 15)
  - Volumes persistem dados do Postgres
- Comandos úteis
  - Rebuild: `docker compose up -d --build`
  - Migrações: 
    - `docker exec beeteller-api python manage.py makemigrations data`
    - `docker exec beeteller-api python manage.py migrate`

### Rotas e roteamento

- `app/beeteller/urls.py`
  - `''` → `health.urls`
  - `'api/'` → `api.urls`
  - `'/api/util/'` → `util.urls`

###Visualização do banco de dados

- Subi o serviço do adminer, disponível em `localhost:8082` para visualização das tabelas do banco de dados