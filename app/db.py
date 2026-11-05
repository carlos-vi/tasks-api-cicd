import os

from sqlalchemy import String, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool


def normalize_database_url(url: str) -> str:
    # Platforms such as Render hand out the URL as "postgres://" or "postgresql://", but with
    # that format SQLAlchemy looks for the old driver (psycopg2). We use psycopg 3,
    # which is selected with "postgresql+psycopg://"
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix) :]
    return url


# The database is chosen with an environment variable. Without it we use SQLite (a file), so the
# app starts without needing anything else. With Docker Compose or Kubernetes it points to PostgreSQL
DATABASE_URL = normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///./tasks.db"))

engine_args: dict = {}
if DATABASE_URL.startswith("sqlite"):
    # SQLite only allows a connection to be used from the thread that created it; FastAPI uses several
    engine_args["connect_args"] = {"check_same_thread": False}
    if DATABASE_URL in ("sqlite://", "sqlite:///:memory:"):
        # In memory, every connection would be a different database: we share a single one
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
    # One session per request: opened on entry and always closed on exit
    with SessionLocal() as session:
        yield session


def create_tables():
    with engine.begin() as conn:
        if engine.dialect.name == "postgresql":
            # With several replicas starting at the same time, all of them would try to create the
            # table and the losers would fail. This lock (the number is arbitrary) lets only one in
            # at a time; it is released automatically when the transaction ends. The others wait
            # and, once inside, see that the table already exists and do nothing
            conn.execute(text("SELECT pg_advisory_xact_lock(1)"))
        Base.metadata.create_all(conn)
