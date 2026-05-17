# IMPORTS
from flask import jsonify, request
from src.models import Board, Task, Lane

# FUNCTION: GET ALL
def get_all(board_id, lane_id):

    # GET BOARD
    board = Board.get_or_none(Board.id == board_id)

    # CHECK FOR BOARD
    if board is None:
        return jsonify({
            "ERROR": "BOARD NOT FOUND"
        }), 404

    # GET LANE FROM BOARD
    lane = Lane.get_or_none(
        (Lane.id == lane_id) &
        (Lane.board == board)
    )

    # CHECK FOR LANE
    if lane is None:
        return jsonify({
            "ERROR": "LANE NOT FOUND IN BOARD"
        }), 404

    # GET TASKS
    tasks = Task.select().where(Task.lane == lane).order_by(Task.id)

    # BUILD TASK LIST
    task_list = []

    # ADD TASKS TO TASK LIST
    for task in tasks:
        task_list.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
        })

    # SEND RESPONSE
    return jsonify(task_list), 200


# FUNCTION: GET BY ID
def get_by_id(board_id, lane_id, task_id):

    # GET BOARD
    board = Board.get_or_none(Board.id == board_id)

    # CHECK FOR BOARD
    if board is None:
        return jsonify({
            "ERROR": "BOARD NOT FOUND"
        }), 404

    # GET LANE FROM BOARD
    lane = Lane.get_or_none(
        (Lane.id == lane_id) &
        (Lane.board == board)
    )

    # CHECK FOR LANE
    if lane is None:
        return jsonify({
            "ERROR": "LANE NOT FOUND IN BOARD"
        }), 404

    # GET TASK FROM LANE
    task = Task.get_or_none(
        (Task.id == task_id) &
        (Task.lane == lane)
    )

    # CHECK FOR TASK
    if task is None:
        return jsonify({
            "ERROR": "TASK NOT FOUND IN LANE"
        }), 404

    # SEND RESPONSE
    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "lane_id": task.lane.id,
        "board_id": task.lane.board.id,
    }), 200


# FUNCTION: CREATE
def create(board_id, lane_id):

    # GET BOARD
    board = Board.get_or_none(Board.id == board_id)

    # CHECK FOR BOARD
    if board is None:
        return jsonify({
            "ERROR": "BOARD NOT FOUND"
        }), 404

    # GET LANE FROM BOARD
    lane = Lane.get_or_none(
        (Lane.id == lane_id) &
        (Lane.board == board)
    )

    # CHECK FOR LANE
    if lane is None:
        return jsonify({
            "ERROR": "LANE NOT FOUND IN BOARD"
        }), 404

    # GET DATA FROM BODY
    data = request.get_json() or {}
    title = data.get("title")
    description = data.get("description")

    # CHECK FOR TITLE
    if not title:
        return jsonify({
            "ERROR": "TITLE IS REQUIRED"
        }), 400

    # CREATE TASK
    task = Task.create(
        title=title,
        description=description,
        lane=lane,
    )

    # SEND RESPONSE
    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
    }), 201

# FUNCTION: UPDATE
def update(board_id, lane_id, task_id):

    # GET BOARD
    board = Board.get_or_none(Board.id == board_id)

    # CHECK FOR BOARD
    if board is None:
        return jsonify({
            "ERROR": "BOARD NOT FOUND"
        }), 404

    # GET LANE FROM BOARD
    lane = Lane.get_or_none(
        (Lane.id == lane_id) &
        (Lane.board == board)
    )

    # CHECK FOR LANE
    if lane is None:
        return jsonify({
            "ERROR": "LANE NOT FOUND IN BOARD"
        }), 404

    # GET TASK FROM LANE
    task = Task.get_or_none(
        (Task.id == task_id) &
        (Task.lane == lane)
    )

    # CHECK FOR TASK
    if task is None:
        return jsonify({
            "ERROR": "TASK NOT FOUND IN LANE"
        }), 404

    # GET DATA FROM BODY
    data = request.get_json() or {}
    title = data.get("title")
    new_lane_id = data.get("lane_id")
    description = data.get("description")

    # UPDATE TITLE
    if "title" in data:
        task.title = title

    # UPDATE DESCRIPTION
    if "description" in data:
        task.description = description

    # UPDATE LANE
    if "lane_id" in data:
        target_lane = Lane.get_or_none(
            (Lane.id == new_lane_id) &
            (Lane.board == board)
        )
        if target_lane is None:
            return jsonify({
                "ERROR": "TARGET LANE NOT FOUND IN BOARD"
            }), 404
        task.lane = target_lane

    # SAVE CHANGES
    task.save()

    # SEND RESPONSE
    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
    }), 200

# FUNCTION: DELETE
def delete(board_id, lane_id, task_id):

    # GET BOARD
    board = Board.get_or_none(Board.id == board_id)

    # CHECK FOR BOARD
    if board is None:
        return jsonify({
            "ERROR": "BOARD NOT FOUND"
        }), 404

    # GET LANE FROM BOARD
    lane = Lane.get_or_none(
        (Lane.id == lane_id) &
        (Lane.board == board)
    )

    # CHECK FOR LANE
    if lane is None:
        return jsonify({
            "ERROR": "LANE NOT FOUND IN BOARD"
        }), 404

    # GET TASK FROM LANE
    task = Task.get_or_none(
        (Task.id == task_id) &
        (Task.lane == lane)
    )

    # CHECK FOR TASK
    if task is None:
        return jsonify({
            "ERROR": "TASK NOT FOUND IN LANE"
        }), 404

    # SAVE TASK DATA BEFORE DELETE
    deleted_task = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
    }

    # DELETE TASK
    task.delete_instance()

    # SEND RESPONSE
    return jsonify(deleted_task), 200
