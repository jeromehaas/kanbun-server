# IMPORTS
from flask import Blueprint
import src.controllers.task_controller as tasks

# CREATE BLUEPRINT
tasks_bp = Blueprint("tasks", __name__)

# ROUTE: GET ALL
@tasks_bp.get("/tasks")
def get_tasks():
    return tasks.get_all()

# ROUTE: GET BY ID
@tasks_bp.get("/tasks/<int:task_id>")
def get_task_by_id(task_id):
    return tasks.get_by_id(task_id)

# ROUTE: CREATE
@tasks_bp.post("/tasks")
def create_task():
    return tasks.create()

# ROUTE: UPDATE
@tasks_bp.patch("/tasks/<int:task_id>")
def update_task(task_id):
    return tasks.update(task_id)

# ROUTE: DELETE
@tasks_bp.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    return tasks.delete(task_id)
