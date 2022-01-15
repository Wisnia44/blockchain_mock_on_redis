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


class Transaction(BaseModel):
    hash: str
    previous_transaction: str
    data: dict
