import os

from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool

# La base de datos se elige con una variable de entorno. Sin ella usamos SQLite (un archivo),
# así la app arranca sin necesitar nada más. Con Docker Compose o Kubernetes se apunta a PostgreSQL.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")

engine_args: dict = {}
if DATABASE_URL.startswith("sqlite"):
    # SQLite solo permite usar una conexión desde el hilo que la creó; FastAPI usa varios
    engine_args["connect_args"] = {"check_same_thread": False}
    if DATABASE_URL in ("sqlite://", "sqlite:///:memory:"):
        # En memoria, cada conexión sería una base de datos distinta: compartimos una sola
        engine_args["poolclass"] = StaticPool

engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))


def get_db():
    # Una sesión por petición: se abre al entrar y se cierra siempre al salir
    with SessionLocal() as session:
        yield session


def create_tables():
    Base.metadata.create_all(engine)
