from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import Task, create_tables, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Se ejecuta una vez al arrancar la app: crea las tablas si no existen
    create_tables()
    yield


app = FastAPI(title="Tasks API experiment", lifespan=lifespan)


class TaskIn(BaseModel):
    title: str


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
