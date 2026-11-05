from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import Task, create_tables, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the app starts: creates the tables if they do not exist
    create_tables()
    yield


app = FastAPI(title="Tasks API experiment", lifespan=lifespan)


class TaskIn(BaseModel):
    # 200 is the size of the column in the database
    title: str = Field(min_length=1, max_length=200)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.scalars(select(Task).order_by(Task.id)).all()
    return [{"id": t.id, "title": t.title} for t in tasks]


@app.post("/tasks", status_code=201)
def create_task(task: TaskIn, db: Session = Depends(get_db)):
    new_task = Task(title=task.title)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"id": new_task.id, "title": new_task.title}


# Serves the web UI (app/static) at "/". It goes LAST on purpose: FastAPI matches routes in
# order, so /health, /tasks and /docs are resolved first and this only catches everything else.
# The path is computed from this file so it works regardless of the working directory
app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
