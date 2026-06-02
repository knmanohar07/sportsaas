from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# --- PLAYER SCHEMAS ---
class PlayerBase(BaseModel):
    name: str
    age: int
    emergency_contact: str
    medical_info: Optional[str] = None

class PlayerCreate(PlayerBase):
    pass  # Used when creating a player (accepts the base data)

class Player(PlayerBase):
    id: int
    joined_date: datetime

    # This tells Pydantic to read database models smoothly
    model_config = ConfigDict(from_attributes=True)


# --- SESSION SCHEMAS ---
class SessionBase(BaseModel):
    turf_name: str
    start_time: datetime
    end_time: datetime
    capacity: int = 20

class SessionCreate(SessionBase):
    pass

class Session(SessionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# --- ATTENDANCE SCHEMAS ---
class AttendanceBase(BaseModel):
    player_id: int
    session_id: int
    attended: bool = False

class AttendanceCreate(AttendanceBase):
    pass

class Attendance(AttendanceBase):
    id: int
    scanned_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- PAYMENT SCHEMAS ---
class PaymentBase(BaseModel):
    player_id: int
    amount_due: float
    amount_paid: float = 0.0
    due_date: datetime
    status: str = "Pending"

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)