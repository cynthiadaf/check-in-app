"""Request and response schemas for guest entries."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.guest import PaymentMethod


def _trim_required(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("must contain non-whitespace characters")
    return value


class GuestEntryCreate(BaseModel):
    """Client fields accepted when creating a guest entry."""

    model_config = ConfigDict(extra="forbid")

    guest_name: str = Field(min_length=1, max_length=200)
    notes: str = Field(min_length=1, max_length=2000)

    @field_validator("guest_name", "notes")
    @classmethod
    def trim_text(cls, value: str) -> str:
        return _trim_required(value)


class GuestEntryUpdate(BaseModel):
    """Client fields accepted when updating a guest entry."""

    model_config = ConfigDict(extra="forbid")

    notes: str | None = Field(default=None, min_length=1, max_length=2000)
    payment_method: PaymentMethod | None = None

    @field_validator("notes")
    @classmethod
    def trim_notes(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("notes cannot be null")
        return _trim_required(value)

    def has_updates(self) -> bool:
        return bool(self.model_fields_set)


class GuestEntryRead(BaseModel):
    """Serialized guest entry."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    register_id: UUID
    guest_name: str
    check_in_time: datetime
    notes: str
    payment_method: PaymentMethod | None
    created_at: datetime
    updated_at: datetime


class PaginatedGuestEntries(BaseModel):
    """Paginated guest-entry response."""

    items: list[GuestEntryRead]
    page: int
    page_size: int
    total: int
    total_pages: int


class RegisterRead(BaseModel):
    """Serialized daily register with its entry count."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    register_date: date
    created_at: datetime


class DashboardRead(BaseModel):
    """Dashboard aggregate response."""

    selected_date: date
    today_guest_count: int
    selected_date_guest_count: int
    most_common_payment_method: PaymentMethod | None
