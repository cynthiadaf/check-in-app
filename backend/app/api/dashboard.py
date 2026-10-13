"""Dashboard endpoint."""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import session_dependency
from app.schemas.guest import DashboardRead
from app.services.guest import GuestService

router = APIRouter()


@router.get("/dashboard", response_model=DashboardRead)
async def get_dashboard(
    date_filter: date | None = Query(default=None, alias="date"),
    session: AsyncSession = Depends(session_dependency),
) -> DashboardRead:
    """Return counts and the most common payment method; ties use enum order."""
    from datetime import datetime, timezone

    return await GuestService(session).dashboard(date_filter or datetime.now(timezone.utc).date())

