"""API contract smoke tests for environments with TEST_DATABASE_URL."""

import pytest


@pytest.mark.integration
def test_postgresql_integration_configuration_is_available(test_database_url: str) -> None:
    """Document the required PostgreSQL integration-test configuration."""
    assert test_database_url.startswith("postgresql+asyncpg://")

