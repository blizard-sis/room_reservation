from datetime import datetime

from pydantic import BaseModel


class ReservationBase(BaseModel):
    from_reserve: datetime
    to_reserve: datetime


class ReservationCreate(ReservationBase):
    meetingroom_id: int


class ReservationUpdate(ReservationBase):
    pass


class ReservationDB(ReservationBase):
    id: int
    meetingroom_id: int

    class Config:
        orm_mode = True