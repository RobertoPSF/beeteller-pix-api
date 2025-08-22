# beeteller-pix-api
Api para gerenciamento de mensagens Pix, o documento contendo as decisões de arquitetura pode ser encontrado [aqui](docs/README.md)

O documento com exemplos de requests e responses pode ser encontrado [aqui](docs/examples.md)

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