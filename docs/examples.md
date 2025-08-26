## Exemplos de requisições e respostas

### GET /health

Resposta 200:
```
{"message": "ok"}
```

### POST /api/util/msgs/{ispb}/{number}

Requisição:
```http
POST /api/util/msgs/32074986/3 HTTP/1.1
Host: localhost:8000
```

Resposta 201:
```json
{ "inserted": 3 }
```

### GET /api/pix/{ispb}/stream/start (Accept: application/json)

Requisição:
```http
GET /api/pix/32074986/stream/start HTTP/1.1
Host: localhost:8000
Accept: application/json
```

Resposta 200:
Headers:
```http
Pull-Next: /api/pix/32074986/stream/17myxj5wskjf
Content-Type: application/json
```
Body:
```json
{
  "endToEndId": "E320749862024022119277T3lEBbUM0z",
  "valor": 90.20,
  "pagador": {
    "nome": "Roberto Filho",
    "cpfCnpj": "98716278190",
    "ispb": "00000000",
    "agencia": "0001",
    "contaTransacional": "1231231",
    "tipoConta": "CACC"
  },
  "recebedor": {
    "nome": "Roberto Pereira",
    "cpfCnpj": "77615678291",
    "ispb": "32074986",
    "agencia": "0361",
    "contaTransacional": "1210098",
    "tipoConta": "SVGS"
  },
  "campoLivre": "",
  "txId": "h7a786d8a7s6gd1hgs",
  "dataHoraPagamento": "2022-07-23T19:47:18.108Z"
}
```

### GET /api/pix/{ispb}/stream/start (Accept: multipart/json)

Requisição:
```http
GET /api/pix/32074986/stream/start HTTP/1.1
Host: localhost:8000
Accept: multipart/json
```

Resposta 200 (até 10 itens):
Headers:
```http
Pull-Next: /api/pix/32074986/stream/17myxj5wskjf
Content-Type: application/json
```
Body:
```json
[
  {
    "endToEndId": "E320749862024022119277T3lEBbUM0z",
    "valor": 90.20,
    "pagador": { "nome": "Marcos José", "cpfCnpj": "98716278190", "ispb": "32074986", "agencia": "0001", "contaTransacional": "1231231", "tipoConta": "CACC" },
    "recebedor": { "nome": "Flavio José", "cpfCnpj": "77615678291", "ispb": "32074986", "agencia": "0361", "contaTransacional": "1210098", "tipoConta": "SVGS" },
    "campoLivre": "",
    "txId": "h7a786d8a7s6gd1hgs",
    "dataHoraPagamento": "2022-07-23T19:47:18.108Z"
  }
]
```

### GET /api/pix/{ispb}/stream/{interationId} (continuação, Accept: application/json)

Requisição:
```http
GET /api/pix/32074986/stream/17myxj5wskjf HTTP/1.1
Host: localhost:8000
Accept: application/json
```

Resposta 200:
Headers:
```http
Pull-Next: /api/pix/32074986/stream/9kp6a6l7c2ii
Content-Type: application/json
```
Body:
```json
{
  "endToEndId": "E320749862024022119277T3lEBbUM0z",
  "valor": 90.20,
  "pagador": { "nome": "Marcos José", "cpfCnpj": "98716278190", "ispb": "00000000", "agencia": "0001", "contaTransacional": "1231231", "tipoConta": "CACC" },
  "recebedor": { "nome": "Flavio José", "cpfCnpj": "77615678291", "ispb": "32074986", "agencia": "0361", "contaTransacional": "1210098", "tipoConta": "SVGS" },
  "campoLivre": "",
  "txId": "h7a786d8a7s6gd1hgs",
  "dataHoraPagamento": "2022-07-23T19:47:18.108Z"
}
```

### GET /api/pix/{ispb}/stream/{interationId} (continuação, Accept: multipart/json)

Requisição:
```http
GET /api/pix/32074986/stream/17myxj5wskjf HTTP/1.1
Host: localhost:8000
Accept: multipart/json
```

Resposta 200 (lista):
Headers:
```http
Pull-Next: /api/pix/32074986/stream/9kp6a6l7c2ii
Content-Type: application/json
```
Body:
```json
[
  {
    "endToEndId": "E320749862024022119277T3lEBbUM0z",
    "valor": 90.20,
    "pagador": { "nome": "Marcos José", "cpfCnpj": "98716278190", "ispb": "32074986", "agencia": "0001", "contaTransacional": "1231231", "tipoConta": "CACC" },
    "recebedor": { "nome": "Flavio José", "cpfCnpj": "77615678291", "ispb": "00000000", "agencia": "0361", "contaTransacional": "1210098", "tipoConta": "SVGS" },
    "campoLivre": "",
    "txId": "h7a786d8a7s6gd1hgs",
    "dataHoraPagamento": "2022-07-23T19:47:18.108Z"
  }
]
```

### GET – Long polling sem mensagens (204)

Requisição:
```http
GET /api/pix/32074986/stream/start HTTP/1.1
Host: localhost:8000
Accept: application/json
```

Resposta 204:
Headers:
```http
Pull-Next: /api/pix/32074986/stream/17myxj5wskjf
```

### DELETE /api/pix/{ispb}/stream/{interationId}

Requisição:
```http
DELETE /api/pix/32074986/stream/9kp6a6l7c2ii HTTP/1.1
Host: localhost:8000
```

Resposta 200:
```json
{}
```


