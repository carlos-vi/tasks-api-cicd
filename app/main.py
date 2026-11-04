from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Tasks API experiment")

tasks: list[dict] = []


class TaskIn(BaseModel):
    title: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    return tasks


@app.post("/tasks", status_code=201)
def create_task(task: TaskIn):
    new_task = {"id": len(tasks) + 1, "title": task.title}
    tasks.append(new_task)
    return new_task
