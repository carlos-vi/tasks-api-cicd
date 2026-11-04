import os

# Debe ir antes de importar la app, que crea la conexión al importarse.
# En local usamos SQLite en memoria; en CI se define DATABASE_URL apuntando a PostgreSQL
os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    # Con "with", FastAPI ejecuta el arranque de la app (y por tanto crea las tablas)
    with TestClient(app) as c:
        yield c
