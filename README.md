# beeteller-pix-api
Api para gerenciamento de mensagens Pix, o documento contendo as decisões de arquitetura pode ser encontrado [aqui](docs/README.md)

## Como executar (Docker)

1) Suba os serviços

```
docker compose up -d --build
```

2) Aplique migrações

```
docker exec beeteller-api python manage.py makemigrations data
docker exec beeteller-api python manage.py migrate
```

- Daqui pra frente sugiro utilizar alguma ferramenta de teste de API interativa, como o Postman

3) Verifique o health

```
http://localhost:8000/health
```

## Endpoints principais

Observação: o header `Accept`, disponível nos métodos GET, controla a quantidade de mensagens retornadas:
- `application/json` → 1 mensagem
- `multipart/json` → até 10 mensagens

### Inserir mensagens de teste

```
http://localhost:8000/util/msgs/{ispb}/{number} - método POST

http://localhost:8000/util/msgs/32074986/5
```

### Iniciar stream

```
http://localhost:8000/api/pix/{ispb}/stream/start - método GET

http://localhost:8000/api/pix/32074986/stream/start
```

A resposta incluirá o header `Pull-Next` com a URL para continuação (interationId).

### Continuar stream

```
http://localhost:8000/api/pix/{ispb}/stream/{interationId} - método GET

http://localhost:8000/api/pix/32074986/stream/<interationId>
```

Quando não houver mensagens em até 8s, o status será 204 com o mesmo `Pull-Next`.

### Encerrar stream

```
http://localhost:8000/api/pix/{ispb}/stream/{interationId} - método DELETE

http://localhost:8000/api/pix/32074986/stream/<interationId>"
```

## Testes

- Para executar os testes, execute o container normalmente
- Depois de já estar rodando, execute o seguinte comando
```
docker exec beeteller-api python manage.py test <app-name>

docker exec beeteller-api python manage.py test health
```

## Dicas

- Caso o host `0.0.0.0` não esteja permitido, ajuste `ALLOWED_HOSTS` no `.env`.
- Para ver as migrações aplicadas:
```
docker exec beeteller-api python manage.py showmigrations data
```
- Para inspecionar tabelas via psql:
```
docker exec -it beeteller-db psql -U beeteller -d pix_db -c "\\dt"
```
- Para ter uma melhor visualização do banco de dados acesse "localhost:8082" (adminer) e faça login com as credenciais usadas na criação do banco de dados.

