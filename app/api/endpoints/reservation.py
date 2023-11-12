from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_meeting_room_exists,
    check_reservation_before_edit,
    check_reservation_intersections,
)
from app.core.db import get_async_session
from app.core.user import current_user
from app.crud.reservation import reservation_crud
from app.models import User
from app.schemas.reservation import (
    ReservationCreate, ReservationDB, ReservationUpdate
)

router = APIRouter()


@router.post('/', response_model=ReservationDB)
async def create_reservation(
        reservation: ReservationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    await check_meeting_room_exists(
        reservation.meetingroom_id, session
    )
    await check_reservation_intersections(
        **reservation.dict(), session=session
    )
    new_reservation = await reservation_crud.create(
        reservation, session, user
    )
    return new_reservation


@router.get('/', response_model=list[ReservationDB])
async def get_all_reservations(
        session: AsyncSession = Depends(get_async_session)
):
    reservations = await reservation_crud.get_multi(session)
    return reservations


@router.get(
    '/{meeting_room_id}/reservations',
    response_model=list[ReservationDB]
)
async def get_reservations_for_room(
        meeting_room_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    await check_meeting_room_exists(meeting_room_id, session)
    reservations = await reservation_crud.get_future_reservations_for_room(
        room_id=meeting_room_id, session=session
    )
    return reservations


@router.patch('/{reservation_id}', response_model=ReservationDB)
async def update_reservation(
        reservation_id: int,
        obj_in: ReservationUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    reservation = await check_reservation_before_edit(
        reservation_id, session
    )
    await check_reservation_intersections(
        **obj_in.dict(),
        reservation_id=reservation_id,
        meetingroom_id=reservation.meetingroom_id,
        session=session
    )
    reservation = await reservation_crud.update(
        db_obj=reservation,
        obj_in=obj_in,
        session=session,
    )
    return reservation


@router.delete('/{reservation_id}', response_model=ReservationDB)
async def delete_reservation(
        reservation_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    reservation = await check_reservation_before_edit(
        reservation_id, session
    )
    reservation = await reservation_crud.remove(
        reservation, session
    )
    return reservation
