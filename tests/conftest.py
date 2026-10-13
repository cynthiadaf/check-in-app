"""Optional PostgreSQL integration-test configuration."""

import os

import pytest


@pytest.fixture
def test_database_url() -> str:
    """Return the disposable PostgreSQL URL configured for integration tests."""
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to run PostgreSQL integration tests")
    return url

