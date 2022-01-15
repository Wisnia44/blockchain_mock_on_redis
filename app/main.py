import json
import logging
from http import HTTPStatus
from typing import List, Optional
from uuid import uuid4

import redis
from cryptography.fernet import Fernet
from fastapi import FastAPI, Response

from app.config import get_settings
from app.models import ComplexEncoder, ParkingSlot, ParkingSlotStatus, Transaction

settings = get_settings()
app = FastAPI(
    title="Blockchain od Redis",
    description="Proof of concept: blockchain centralized database based on Redis with REST API interface",
)
r = redis.Redis(host="redis", port=6379)
logging.basicConfig(level="INFO")
f = Fernet(settings.fernet_key_url_safe_base64_encoded)
app.last_transaction_hash = "0"


@app.post("/new-status/", response_model=Transaction)
async def change_parking_slot_status(parking_slot: ParkingSlot):
    transaction_hash = uuid4().hex
    transaction = Transaction(
        hash=transaction_hash,
        previous_transaction=app.last_transaction_hash,
        data=parking_slot,
    )
    r.set(
        name=transaction_hash,
        value=f.encrypt(
            json.dumps(transaction.reprJSON(), cls=ComplexEncoder).encode("utf-8")
        ),
    )
    app.last_transaction_hash = transaction_hash
    return transaction


@app.get("/get-transaction/", response_model=Optional[Transaction])
async def get_transaction(hash: str):
    item = r.get(hash)
    if not item:
        return Response(
            status_code=HTTPStatus.NOT_FOUND.value,
            content=f"Transaction with hash {hash} not found",
        )

    item_dict = json.loads(f.decrypt(item))
    return Transaction(**item_dict)


@app.get("/get-all-transactions/", response_model=List[Transaction])
async def get_all_transactions():
    current_transaction_hash = app.last_transaction_hash
    transactions = []
    while current_transaction_hash != "0":
        item = r.get(current_transaction_hash)
        item_dict = json.loads(f.decrypt(item))
        transaction = Transaction(**item_dict)
        transactions.append(transaction)
        current_transaction_hash = transaction.previous_transaction
    return transactions


@app.get("/get-parking-slot-status/", response_model=Optional[ParkingSlotStatus])
async def get_parking_slot_status(id: str):
    current_transaction_hash = app.last_transaction_hash
    while current_transaction_hash != "0":
        item = r.get(current_transaction_hash)
        item_dict = json.loads(f.decrypt(item))
        transaction = Transaction(**item_dict)
        if transaction.data.id == id:
            return transaction.data.status
        current_transaction_hash = transaction.previous_transaction
    return Response(
        status_code=HTTPStatus.NOT_FOUND.value,
        content=f"Parking slot with id {id} not found",
    )
