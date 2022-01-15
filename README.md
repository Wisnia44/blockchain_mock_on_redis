# Blockchain mock on redis

Proof of concept: blockchain centralized database based on Redis with REST API interface.\
Serves storing and verifying parking slot occupation state.\
No deletions allowed.

## API docs

Full API docs could be found on: `http://127.0.0.1/docs`

## Possible operations

### new-status

Usage:

```curl
curl --location --request POST 'http://0.0.0.0:8000/new-status/' \
--header 'Content-Type: application/json' \
--data-raw '{
  "id": "123456",
  "status": "free"
}'
```

### get-transaction

Usage:

```curl
curl --location --request GET 'http://0.0.0.0:8000/get-transaction/?hash=50e2c62e26e44aa98454663be7bae74d'
```

### get-all-transactions

Usage:

```curl
curl --location --request GET 'http://0.0.0.0:8000/get-all-transactions/'
```

### get-parking-slot-status

Usage:

```curl
curl --location --request GET 'http://0.0.0.0:8000/get-parking-slot-status/?id=123456'
```
