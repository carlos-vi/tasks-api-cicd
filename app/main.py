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
    # Se ejecuta una vez al arrancar la app: crea las tablas si no existen
    create_tables()
    yield


app = FastAPI(title="Tasks API experiment", lifespan=lifespan)


class TaskIn(BaseModel):
    # 200 es el tamaño de la columna en la base de datos
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


# Sirve la interfaz web (app/static) en "/". Va al FINAL a propósito: FastAPI atiende las rutas
# en orden, así que /health, /tasks y /docs se resuelven antes y esto solo recoge el resto.
# La ruta se calcula a partir de este archivo para que funcione desde cualquier carpeta
app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
