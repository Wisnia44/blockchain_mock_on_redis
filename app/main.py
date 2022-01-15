import json
import logging
from typing import List
from uuid import uuid4

import redis
from cryptography.fernet import Fernet
from fastapi import FastAPI

from app.config import get_settings
from app.models import ParkingSlot, ParkingSlotStatus, Transaction

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
        data=parking_slot.__dict__,
    )
    r.set(
        name=transaction_hash, value=f.encrypt(json.dumps(transaction.__dict__).encode("utf-8"))
    )
    app.last_transaction_hash = transaction_hash
    logging.info("New last_transaction_hash is %s", app.last_transaction_hash)
    return transaction


@app.get("/get-transaction/", response_model=ParkingSlot)
async def get_transaction(hash: str):
    parking_slot = ParkingSlot(id="1", status=ParkingSlotStatus.FREE.value)
    return parking_slot


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


@app.get("/get-parking-slot-status/", response_model=ParkingSlotStatus)
async def get_parking_slot_status(id: str):
    return ParkingSlotStatus.FREE.value
