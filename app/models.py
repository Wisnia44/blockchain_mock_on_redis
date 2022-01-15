import json
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ParkingSlotStatus(str, Enum):
    FREE = "free"
    LOCKED = "locked"
    MAINTENANCE = "maintenance"
    OCCUPIED = "occupied"


class ParkingSlot(BaseModel):
    id: str
    status: ParkingSlotStatus
    occupied_by_car: Optional[str]

    def reprJSON(self):
        return dict(
            id=self.id, status=self.status, occupied_by_car=self.occupied_by_car
        )


class Transaction(BaseModel):
    hash: str
    previous_transaction: str
    data: ParkingSlot

    def reprJSON(self):
        return dict(
            hash=self.hash,
            previous_transaction=self.previous_transaction,
            data=self.data,
        )


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "reprJSON"):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)
