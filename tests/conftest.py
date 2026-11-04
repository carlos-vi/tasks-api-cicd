import os

# This must come before importing the app, which creates its database connection on import.
# Locally we use in-memory SQLite; in CI, DATABASE_URL is set to point at PostgreSQL
os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    # With "with", FastAPI runs the app startup (and therefore creates the tables)
    with TestClient(app) as c:
        yield c
