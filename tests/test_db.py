import pytest

from app.db import normalize_database_url


@pytest.mark.parametrize(
    "url, expected",
    [
        # Formats handed out by platforms such as Render
        ("postgres://u:p@host/db", "postgresql+psycopg://u:p@host/db"),
        ("postgresql://u:p@host:5432/db", "postgresql+psycopg://u:p@host:5432/db"),
        # The driver is already specified: left untouched
        ("postgresql+psycopg://u:p@db:5432/tasks", "postgresql+psycopg://u:p@db:5432/tasks"),
        # SQLite is left untouched
        ("sqlite:///./tasks.db", "sqlite:///./tasks.db"),
        ("sqlite://", "sqlite://"),
    ],
)
def test_normalize_database_url(url, expected):
    assert normalize_database_url(url) == expected
