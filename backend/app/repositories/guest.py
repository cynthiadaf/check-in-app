"""Repository operations for guest registers and entries."""

from datetime import date
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.guest import DailyGuestRegister, GuestEntry, PaymentMethod


class GuestRepository:
    """Encapsulates database queries for the guest domain."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create_register(self, register_date: date) -> DailyGuestRegister:
        """Return a register, safely creating it when absent."""
        result = await self.session.execute(
            select(DailyGuestRegister).where(DailyGuestRegister.register_date == register_date)
        )
        register = result.scalar_one_or_none()
        if register:
            return register
        register = DailyGuestRegister(register_date=register_date)
        self.session.add(register)
        try:
            await self.session.flush()
        except Exception:
            await self.session.rollback()
            result = await self.session.execute(
                select(DailyGuestRegister).where(DailyGuestRegister.register_date == register_date)
            )
            register = result.scalar_one()
        return register

    async def create_entry(self, entry: GuestEntry) -> GuestEntry:
        self.session.add(entry)
        await self.session.flush()
        await self.session.refresh(entry)
        return entry

    async def get_entry(self, entry_id: UUID) -> GuestEntry | None:
        return await self.session.get(GuestEntry, entry_id)

    async def list_registers(self) -> list[DailyGuestRegister]:
        result = await self.session.execute(
            select(DailyGuestRegister).order_by(DailyGuestRegister.register_date.desc())
        )
        return list(result.scalars().all())

    async def get_register(self, register_date: date) -> DailyGuestRegister | None:
        result = await self.session.execute(
            select(DailyGuestRegister).where(DailyGuestRegister.register_date == register_date)
        )
        return result.scalar_one_or_none()

    async def list_entries(
        self, register_date: date | None, search: str | None, page: int, page_size: int
    ) -> tuple[list[GuestEntry], int]:
        query = select(GuestEntry).join(GuestEntry.register)
        count_query = select(func.count(GuestEntry.id)).join(GuestEntry.register)
        if register_date:
            query = query.where(DailyGuestRegister.register_date == register_date)
            count_query = count_query.where(DailyGuestRegister.register_date == register_date)
        if search:
            condition = GuestEntry.guest_name.ilike(f"%{search}%")
            query = query.where(condition)
            count_query = count_query.where(condition)
        total = int((await self.session.execute(count_query)).scalar_one())
        result = await self.session.execute(
            query.order_by(GuestEntry.check_in_time.desc(), GuestEntry.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def payment_counts(self, register_date: date) -> list[tuple[PaymentMethod, int]]:
        result = await self.session.execute(
            select(GuestEntry.payment_method, func.count(GuestEntry.id))
            .join(GuestEntry.register)
            .where(
                DailyGuestRegister.register_date == register_date,
                GuestEntry.payment_method.is_not(None),
            )
            .group_by(GuestEntry.payment_method)
            .order_by(func.count(GuestEntry.id).desc(), GuestEntry.payment_method.asc())
        )
        return [(method, count) for method, count in result.all() if method is not None]

    async def count_for_date(self, register_date: date) -> int:
        result = await self.session.execute(
            select(func.count(GuestEntry.id))
            .join(GuestEntry.register)
            .where(DailyGuestRegister.register_date == register_date)
        )
        return int(result.scalar_one())

