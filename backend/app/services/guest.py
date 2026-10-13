"""Guest register business services."""

from datetime import date, datetime, timezone
from math import ceil
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.guest import GuestEntry
from app.repositories.guest import GuestRepository
from app.schemas.guest import (
    DashboardRead,
    GuestEntryCreate,
    GuestEntryUpdate,
    PaginatedGuestEntries,
)


class GuestService:
    """Applies business rules to guest entry operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.repository = GuestRepository(session)
        self.session = session

    async def create(self, data: GuestEntryCreate) -> GuestEntry:
        now = datetime.now(timezone.utc)
        register = await self.repository.get_or_create_register(now.date())
        entry = GuestEntry(
            register=register,
            guest_name=data.guest_name,
            notes=data.notes,
            check_in_time=now,
        )
        created = await self.repository.create_entry(entry)
        await self.session.commit()
        return created

    async def list_entries(
        self, register_date: date | None, search: str | None, page: int, page_size: int
    ) -> PaginatedGuestEntries:
        entries, total = await self.repository.list_entries(
            register_date, search.strip() if search else None, page, page_size
        )
        return PaginatedGuestEntries(
            items=entries,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=ceil(total / page_size) if total else 0,
        )

    async def update(self, entry: GuestEntry, data: GuestEntryUpdate) -> GuestEntry:
        changes = data.model_dump(exclude_unset=True)
        for field, value in changes.items():
            setattr(entry, field, value)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry

    async def delete(self, entry: GuestEntry) -> None:
        await self.session.delete(entry)
        await self.session.commit()

    async def dashboard(self, selected_date: date) -> DashboardRead:
        counts = await self.repository.payment_counts(selected_date)
        return DashboardRead(
            selected_date=selected_date,
            today_guest_count=await self.repository.count_for_date(datetime.now(timezone.utc).date()),
            selected_date_guest_count=await self.repository.count_for_date(selected_date),
            most_common_payment_method=counts[0][0] if counts else None,
        )

