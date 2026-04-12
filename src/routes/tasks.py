# IMPORTS
from flask import Blueprint
import src.controllers.tasks as tasks

# CREATE BLUEPRINT
tasks_bp = Blueprint("tasks", __name__)

# GET ALL TASKS IN A LANE
@tasks_bp.get("/boards/<int:board_id>/lanes/<int:lane_id>/tasks")
def get_tasks(board_id, lane_id):
    return tasks.get_all(board_id, lane_id)

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
