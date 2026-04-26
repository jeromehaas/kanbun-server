# IMPORTS
from flask import jsonify, request
from peewee import prefetch
from src.models import Board, Task, Lane

# FUNCTION: GET ALL
def get_all():

    # PREFETCH ALL BOARDS WITH LANES AND TASKS
    boards = prefetch(
        Board.select().order_by(Board.id),
        Lane.select().order_by(Lane.position),
        Task.select().order_by(Task.id)
    )

    # SETUP BOARD LIST
    board_list = []

    # LOOP OVER BOARDS
    for board in boards:

        # SETUP LANE LIST
        lane_list = []

        # LOOP OVER LANES
        for lane in board.lanes:

            # SETUP TASK LIST
            task_list = []

            # LOOP OVER TASKS
            for task in lane.tasks:
                task_list.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                })

            # ADD LANE TO LANE LIST
            lane_list.append({
                "id": lane.id,
                "name": lane.name,
                "position": lane.position,
                "tasks": task_list,
            })

        # ADD BOARD TO BOARD LIST
        board_list.append({
            "id": board.id,
            "name": board.name,
            "lanes": lane_list,
        })

    # SEND RESPONSE
    return jsonify(board_list), 200


# FUNCTION: GET BY ID
def get_by_id(board_id):

    # PREFETCH BOARD WITH LANES AND TASKS
    boards = prefetch(
        Board.select().where(Board.id == board_id),
        Lane.select().order_by(Lane.position),
        Task.select().order_by(Task.id)
    )

    # EXTRACT SINGLE BOARD
    board = next(iter(boards), None)

    # CHECK FOR BOARD
    if board is None:
        return jsonify({
            "ERROR": "BOARD NOT FOUND"
        }), 404

    # SETUP LANE LIST
    lane_list = []

    # LOOP OVER LANES
    for lane in board.lanes:

        # SETUP TASK LIST
        task_list = []

        # LOOP OVER TASKS
        for task in lane.tasks:

            # ADD TASKS TO TASK LIST
            task_list.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
            })

        # ADD LANE TO LANE LIST
        lane_list.append({
            "id": lane.id,
            "name": lane.name,
            "position": lane.position,
            "tasks": task_list,
        })

    # SEND RESPONSE
    return jsonify({
        "id": board.id,
        "name": board.name,
        "lanes": lane_list,
    }), 200

# FUNCTION: CREATE
def create():

    # GET DATA FROM BODY
    data = request.get_json() or {}
    name = data.get("name")

    # CHECK FOR NAME ATTRIBUTE
    if not name:
        return jsonify({
            "ERROR": "BOARD NAME IS REQUIRED"
        }), 400

    # CHECK FOR EXISTING BOARD
    existing_board = Board.get_or_none(Board.name == name)

    # CHECK FOR EXISTING BOARD
    if existing_board is not None:
        return jsonify({
            "ERROR": "BOARD WITH THIS NAME ALREADY EXISTS"
        }), 400

    # CREATE NEW BOARD
    board = Board.create(
        name=name
    )

    # DEFINE DEFAULT LANES
    default_lanes = [
        "Open",
        "In Progress",
        "Review",
        "Done",
    ]

    # SETUP LANE LIST
    lane_list = []

    # LOOP OVER DEFAULT LANES
    for position, lane_name in enumerate(default_lanes, start=1):

        # CREATE LANES
        lane = Lane.create(
            board=board,
            name=lane_name,
            position=position
        )

        # APPEND LANE TO LANE LIST
        lane_list.append({
            "id": lane.id,
            "name": lane.name,
            "position": lane.position,
            "tasks": [],
        })

    # SEND RESPONSE
    return jsonify({
        "id": board.id,
        "name": board.name,
        "lanes": lane_list,
    }), 201

# FUNCTION: UPDATE
def update(board_id):

    # GET BOARD
    board = Board.get_or_none(Board.id == board_id)

    # CHECK FOR BOARD
    if board is None:
        return jsonify({
            "ERROR": "BOARD NOT FOUND"
        }), 404

    # GET DATA FROM BODY
    data = request.get_json() or {}
    name = data.get("name")

    # CHECK FOR NAME
    if name is None:
        return jsonify({
            "ERROR": "BOARD NAME CANNOT BE EMPTY"
        }), 400

    # CHECK FOR BOARD WITH SAME NAME
    existing_board = Board.get_or_none(
        (Board.name == name) &
        (Board.id != board_id)
    )

    # CHECK FOR BOARD
    if existing_board is not None:
        return jsonify({
            "ERROR": "BOARD WITH THIS NAME ALREADY EXISTS"
        }), 400

    # GET NAME
    board.name = name

    # SAVE CHANGES
    board.save()

    # PREFETCH UPDATED BOARD WITH LANES AND TASKS
    boards = prefetch(
        Board.select().where(Board.id == board_id),
        Lane.select().order_by(Lane.position),
        Task.select().order_by(Task.id)
    )

    # EXTRACT SINGLE BOARD
    updated_board = next(iter(boards), None)

    # SAFETY CHECK
    if updated_board is None:
        return jsonify({
            "ERROR": "BOARD NOT FOUND"
        }), 404

    # SETUP LANE LIST
    lane_list = []

    # LOOP OVER LANES
    for lane in updated_board.lanes:

        # SETUP TASK LIST
        task_list = []

        # LOOP OVER TASKS
        for task in lane.tasks:
            task_list.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
            })

        # ADD LANE TO LANE LIST
        lane_list.append({
            "id": lane.id,
            "name": lane.name,
            "position": lane.position,
            "tasks": task_list,
        })

    # SEND RESPONSE
    return jsonify({
        "id": updated_board.id,
        "name": updated_board.name,
        "lanes": lane_list,
    }), 200

# FUNCTION: DELETE
def delete(board_id):

    # GET BOARD
    board = Board.get_or_none(Board.id == board_id)

    # CHECK FOR BOARD
    if board is None:
        return jsonify({
            "ERROR": "BOARD NOT FOUND"
        }), 404

    # SAVE DELETED BOARD
    deleted_board = {
        "id": board.id,
        "name": board.name,
    }

    # DELETE BOARD WITH RELATED LANES AND TASKS
    board.delete_instance(recursive=True)

    # SEND RESPONSE
    return jsonify(
        deleted_board
    ), 200
