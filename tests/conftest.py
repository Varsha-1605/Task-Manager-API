import pytest
from main import tasks_db


@pytest.fixture(autouse=True)
def clear_tasks_db():
    tasks_db.clear()
    yield
    tasks_db.clear()