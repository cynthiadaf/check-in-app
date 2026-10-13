"""Focused schema tests that run without external services."""

import pytest
from pydantic import ValidationError

from app.schemas.guest import GuestEntryCreate, GuestEntryUpdate


def test_create_trims_text() -> None:
    data = GuestEntryCreate(guest_name=" Ada ", notes=" Welcome ")
    assert data.guest_name == "Ada"
    assert data.notes == "Welcome"


def test_blank_values_are_rejected() -> None:
    with pytest.raises(ValidationError):
        GuestEntryCreate(guest_name=" ", notes="note")
    with pytest.raises(ValidationError):
        GuestEntryCreate(guest_name="Ada", notes=" ")


def test_update_rejects_extra_server_fields() -> None:
    with pytest.raises(ValidationError):
        GuestEntryUpdate.model_validate({"guest_name": "Changed"})

