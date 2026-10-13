"""Guest-entry and register endpoints."""

from datetime import date
from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import session_dependency
from app.repositories.guest import GuestRepository
from app.schemas.guest import (
    GuestEntryCreate,
    GuestEntryRead,
    GuestEntryUpdate,
    PaginatedGuestEntries,
    RegisterRead,
)
from app.services.guest import GuestService

router = APIRouter()


def not_found() -> HTTPException:
    return HTTPException(status_code=404, detail={"detail": "Guest entry not found", "code": "GUEST_ENTRY_NOT_FOUND"})


@router.get("/registers", response_model=list[RegisterRead])
async def get_registers(session: AsyncSession = Depends(session_dependency)) -> list[RegisterRead]:
    return await GuestRepository(session).list_registers()


@router.get("/registers/{register_date}", response_model=RegisterRead)
async def get_register(register_date: date, session: AsyncSession = Depends(session_dependency)) -> RegisterRead:
    register = await GuestRepository(session).get_register(register_date)
    if register is None:
        raise HTTPException(status_code=404, detail={"detail": "Register not found", "code": "REGISTER_NOT_FOUND"})
    return register


@router.get("/guest-entries", response_model=PaginatedGuestEntries)
async def list_entries(
    date_filter: date | None = Query(default=None, alias="date"),
    search: str | None = Query(default=None, max_length=200),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    session: AsyncSession = Depends(session_dependency),
) -> PaginatedGuestEntries:
    return await GuestService(session).list_entries(date_filter, search, page, page_size)


@router.get("/guest-entries/{entry_id}", response_model=GuestEntryRead)
async def get_entry(entry_id: UUID, session: AsyncSession = Depends(session_dependency)) -> GuestEntryRead:
    entry = await GuestRepository(session).get_entry(entry_id)
    if entry is None:
        raise not_found()
    return entry


@router.post("/guest-entries", response_model=GuestEntryRead, status_code=status.HTTP_201_CREATED)
async def create_entry(data: GuestEntryCreate, session: AsyncSession = Depends(session_dependency)) -> GuestEntryRead:
    return await GuestService(session).create(data)


@router.patch("/guest-entries/{entry_id}", response_model=GuestEntryRead)
async def update_entry(
    entry_id: UUID, data: GuestEntryUpdate, session: AsyncSession = Depends(session_dependency)
) -> GuestEntryRead:
    if not data.has_updates():
        raise HTTPException(status_code=422, detail={"detail": "At least one field is required", "code": "EMPTY_UPDATE"})
    entry = await GuestRepository(session).get_entry(entry_id)
    if entry is None:
        raise not_found()
    return await GuestService(session).update(entry, data)


@router.delete("/guest-entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(entry_id: UUID, session: AsyncSession = Depends(session_dependency)) -> Response:
    entry = await GuestRepository(session).get_entry(entry_id)
    if entry is None:
        raise not_found()
    await GuestService(session).delete(entry)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

