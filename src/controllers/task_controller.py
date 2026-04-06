# IMPORTS
from flask import jsonify, request
from src.models import Board, Task, Lane

# FUNCTION: GET ALL
def get_all():

    # GET ALL TASKS
    tasks = Task.select()

    # DEFINE TASKS LIST
    tasks_list = []

    # ADD TASKS TO TASKS LIST
    for task in tasks:
        tasks_list.append({
            "id": task.id,
            "title": task.title,
            "board_id": task.board.id,
        })

    # SEND RESPONSE
    return jsonify(
        tasks_list,
    ), 200

# FUNCTION: GET BY ID
def get_by_id(task_id):

    # GET TASK
    task = Task.get_or_none(Task.id == task_id)

   # CHECK FOR TASK
    if task is None:
        return jsonify(
            {"💥ERROR": "TASK NOT FOUND"}
        ), 404

    # SEND RESPONSE
    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
    },
    ), 200

# FUNCTION:
def create():

    # GET DATA FROM BODY
    data = request.get_json() or {}
    title = data.get("title")
    description = data.get("description")
    lane_id = data.get("lane_id")
    board_id = data.get("board_id")

    # CHECK FOR TITLE ATTRIBUTE
    if not title or not board_id or not lane_id:
        return jsonify(
            {"💥ERROR": "TITLE AND BOARD_ID ARE REQUIRED"}
        ), 400

    # GET BOARD RELATED TO TASK
    board = Board.get_or_none(Board.id == board_id)

    # CHECK FOR BOARD
    if board is None:
        return jsonify({
            "💥ERROR": "BOARD NOT FOUND"
        }), 404

    # GET LANE AND MAKE SURE IT BELONGS TO BOARD
    lane = Lane.get_or_none((Lane.id == lane_id) & (Lane.board == board))

    # CHECK FOR LANE
    if lane is None:
        return jsonify({
            "💥ERROR": "LANE NOT FOUND FOR THIS BOARD"
        }), 404


    # CREATE TASK
    task = Task.create(
        title=title,
        board=board,
        lane=lane,
        description=description,
    )

    # SEND RESPONSE
    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "board_id": board.id,
    }), 201

# FUNCTION: UPDATE
def update(task_id):

    # GET TASK
    task = Task.get_or_none(Task.id == task_id)

    # CHECK FOR TASK
    if task is None:
        return jsonify(
            {"💥ERROR": "TASK NOT FOUND"}
        ), 404

    # GET DATA FROM BODY
    data = request.get_json() or {}

    # DETERMINE TARGET BOARD ID
    target_board_id = data.get("board_id", task.board.id)

    # GET TARGET BOARD
    board = Board.get_or_none(Board.id == target_board_id)

    # CHECK FOR BOARD
    if board is None:
        return jsonify({
            "💥ERROR": "BOARD NOT FOUND"
        }), 404

    # DETERMINE TARGET LANE ID
    target_lane_id = data.get("lane_id", task.lane.id)

    # GET TARGET LANE AND MAKE SURE IT BELONGS TO BOARD
    lane = Lane.get_or_none(
        (Lane.id == target_lane_id) &
        (Lane.board == board)
    )

    # CHECK FOR LANE
    if lane is None:
        return jsonify({
            "💥ERROR": "LANE NOT FOUND FOR THIS BOARD"
        }), 404

    # UPDATE OPTIONAL ATTRIBUTES
    if "title" in data:
        task.title = data["title"]

    if "description" in data:
        task.description = data["description"]

    # UPDATE RELATIONS
    task.board = board
    task.lane = lane

    # SAVE CHANGES
    task.save()

    # SEND RESPONSE
    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "board_id": task.board.id,
        "lane_id": task.lane.id,
    }), 200


# FUNCTION: DELETE
def delete(task_id):

    # GET TASK
    task = Task.get_or_none(Task.id == task_id)

    # CHECK FOR TASK
    if task is None:
        return jsonify({
            "💥ERROR": "TASK NOT FOUND"
        }), 404

    # SAVE TASK DATA BEFORE DELETE
    deleted_task = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "board_id": task.board.id,
        "lane_id": task.lane.id,
    }

    # DELETE TASK
    task.delete_instance()

    # SEND RESPONSE
    return jsonify(
        deleted_task
    ), 200
