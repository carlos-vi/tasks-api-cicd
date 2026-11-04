import os

from sqlalchemy import String, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool

# La base de datos se elige con una variable de entorno. Sin ella usamos SQLite (un archivo),
# así la app arranca sin necesitar nada más. Con Docker Compose o Kubernetes se apunta a PostgreSQL.


def normalize_database_url(url: str) -> str:
    # Plataformas como Render entregan la URL como "postgres://" o "postgresql://", pero con ese
    # formato SQLAlchemy busca el driver antiguo (psycopg2). Nosotros usamos psycopg 3,
    # que se indica con "postgresql+psycopg://"
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix) :]
    return url


DATABASE_URL = normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///./tasks.db"))

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
    with engine.begin() as conn:
        if engine.dialect.name == "postgresql":
            # Con varias réplicas arrancando a la vez, todas intentarían crear la tabla y las
            # perdedoras fallarían. Este candado (el número es arbitrario) hace que solo una
            # entre cada vez; se libera solo al terminar la transacción. Las demás esperan y,
            # al entrar, ven que la tabla ya existe y no hacen nada
            conn.execute(text("SELECT pg_advisory_xact_lock(1)"))
        Base.metadata.create_all(conn)
