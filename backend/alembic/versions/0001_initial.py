"""Create guest register tables."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    payment_enum = postgresql.ENUM(
        "CASH", "CARD", "BANK_TRANSFER", "MOBILE_PAYMENT", "MEMBERSHIP", "NONE", "OTHER",
        name="payment_method",
    )
    payment_enum.create(op.get_bind(), checkfirst=True)
    table_payment_enum = postgresql.ENUM(
        "CASH", "CARD", "BANK_TRANSFER", "MOBILE_PAYMENT", "MEMBERSHIP", "NONE", "OTHER",
        name="payment_method", create_type=False,
    )
    op.create_table(
        "daily_guest_registers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("register_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("register_date", name="uq_daily_guest_register_date"),
    )
    op.create_index("ix_daily_guest_registers_register_date", "daily_guest_registers", ["register_date"], unique=True)
    op.create_table(
        "guest_entries",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("register_id", sa.UUID(), nullable=False),
        sa.Column("guest_name", sa.String(length=200), nullable=False),
        sa.Column("check_in_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("payment_method", table_payment_enum, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["register_id"], ["daily_guest_registers.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_guest_entries_register_id", "guest_entries", ["register_id"], unique=False)
    op.create_index("ix_guest_entries_check_in_time", "guest_entries", ["check_in_time"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_guest_entries_check_in_time", table_name="guest_entries")
    op.drop_index("ix_guest_entries_register_id", table_name="guest_entries")
    op.drop_table("guest_entries")
    op.drop_index("ix_daily_guest_registers_register_date", table_name="daily_guest_registers")
    op.drop_table("daily_guest_registers")
    postgresql.ENUM(name="payment_method").drop(op.get_bind(), checkfirst=True)

