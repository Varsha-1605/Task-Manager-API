"""
Task Manager API
-----------------
A simple FastAPI application demonstrating a full set of CRUD (Create, Read,
Update, Delete) endpoints, request/response validation with Pydantic,
proper HTTP status codes, and basic error handling.

Run locally:
    pip install -r requirements.txt
    uvicorn main:app --reload

Then open http://127.0.0.1:8000/docs for interactive Swagger UI.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Task Manager API",
    description="A simple CRUD API for managing tasks, built with FastAPI.",
    version="1.0.0",
)

# Allow all origins for local development/demo purposes.
# Restrict this list before deploying to production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, example="Write report")
    description: Optional[str] = Field(None, max_length=1000)
    priority: TaskPriority = TaskPriority.medium
    completed: bool = False


class TaskCreate(TaskBase):
    """Fields accepted when creating a task."""
    pass


class TaskUpdate(BaseModel):
    """Fields accepted when updating a task. All fields are optional."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[TaskPriority] = None
    completed: Optional[bool] = None


class Task(TaskBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# "Database" — in-memory store for demo purposes.
# Swap this out for a real database (e.g. PostgreSQL + SQLAlchemy) in production.
# ---------------------------------------------------------------------------

tasks_db: dict[UUID, Task] = {}

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/", tags=["Health"])
def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "message": "Task Manager API is running"}

@app.get("/welcome", tags=["Welcome"])
def welcome():
    """Welcome message."""
    return {"message": "Welcome to the Task Manager API"}


@app.get("/tasks", response_model=list[Task], tags=["Tasks"])
def list_tasks(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
):
    """List all tasks, optionally filtered by completion status and/or priority."""
    results = list(tasks_db.values())

    if completed is not None:
        results = [t for t in results if t.completed == completed]
    if priority is not None:
        results = [t for t in results if t.priority == priority]

    return results


@app.get("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
def get_task(task_id: UUID):
    """Retrieve a single task by its ID."""
    task = tasks_db.get(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def create_task(payload: TaskCreate):
    """Create a new task."""
    now = datetime.utcnow()
    task = Task(id=uuid4(), created_at=now, updated_at=now, **payload.model_dump())
    tasks_db[task.id] = task
    return task


@app.put("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
def update_task(task_id: UUID, payload: TaskUpdate):
    """Update one or more fields of an existing task."""
    existing = tasks_db.get(task_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    update_data = payload.model_dump(exclude_unset=True)
    updated = existing.model_copy(update={**update_data, "updated_at": datetime.utcnow()})
    tasks_db[task_id] = updated
    return updated


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
def delete_task(task_id: UUID):
    """Delete a task by its ID."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    del tasks_db[task_id]
    return None