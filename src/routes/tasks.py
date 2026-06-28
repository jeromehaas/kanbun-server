# IMPORTS
from flask import Blueprint
import src.controllers.tasks as tasks
from src.services.auth_service import require_http_auth

# CREATE BLUEPRINT
tasks_bp = Blueprint("tasks", __name__)

# HOOK: REQUIRE AUTHENTICATION
@tasks_bp.before_request
def authenticate_task_requests():
    return require_http_auth()

# GET ALL TASKS IN A LANE
@tasks_bp.get("/boards/<int:board_id>/lanes/<int:lane_id>/tasks")
def get_tasks(board_id, lane_id):
    return tasks.get_all(board_id, lane_id)

# SEARCH TASKS ACROSS ALL BOARDS
@tasks_bp.get("/tasks/search")
def search_tasks():
    return tasks.search()

# GET ONE TASK IN A LANE
@tasks_bp.get("/boards/<int:board_id>/lanes/<int:lane_id>/tasks/<int:task_id>")
def get_task_by_id(board_id, lane_id, task_id):
    return tasks.get_by_id(board_id, lane_id, task_id)

# CREATE TASK IN A LANE
@tasks_bp.post("/boards/<int:board_id>/lanes/<int:lane_id>/tasks")
def create_task(board_id, lane_id):
    return tasks.create(board_id, lane_id)

# UPDATE TASK IN A LANE
@tasks_bp.patch("/boards/<int:board_id>/lanes/<int:lane_id>/tasks/<int:task_id>")
def update_task(board_id, lane_id, task_id):
    return tasks.update(board_id, lane_id, task_id)

# DELETE TASK IN A LANE
@tasks_bp.delete("/boards/<int:board_id>/lanes/<int:lane_id>/tasks/<int:task_id>")
def delete_task(board_id, lane_id, task_id):
    return tasks.delete(board_id, lane_id, task_id)
