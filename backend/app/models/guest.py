"""Guest register domain models."""

from datetime import date, datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import Date, DateTime, Enum as SqlEnum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin, utc_now


class PaymentMethod(str, Enum):
    """Payment methods supported by the API."""

    CASH = "CASH"
    CARD = "CARD"
    BANK_TRANSFER = "BANK_TRANSFER"
    MOBILE_PAYMENT = "MOBILE_PAYMENT"
    MEMBERSHIP = "MEMBERSHIP"
    NONE = "NONE"
    OTHER = "OTHER"


class DailyGuestRegister(UUIDPrimaryKeyMixin, Base):
    """The automatically-created register for one UTC calendar day."""

    __tablename__ = "daily_guest_registers"
    __table_args__ = (UniqueConstraint("register_date", name="uq_daily_guest_register_date"),)

    register_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    entries: Mapped[list["GuestEntry"]] = relationship(back_populates="register")


class GuestEntry(UUIDPrimaryKeyMixin, Base):
    """A guest's check-in within a daily register."""

    __tablename__ = "guest_entries"

    register_id: Mapped[UUID] = mapped_column(
        ForeignKey("daily_guest_registers.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    guest_name: Mapped[str] = mapped_column(String(200), nullable=False)
    check_in_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    payment_method: Mapped[PaymentMethod | None] = mapped_column(
        SqlEnum(PaymentMethod, name="payment_method", values_callable=lambda enum: [item.value for item in enum]),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )
    register: Mapped[DailyGuestRegister] = relationship(back_populates="entries")

