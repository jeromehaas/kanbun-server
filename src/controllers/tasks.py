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

    # GET TASKS ORDERED BY POSITION
    tasks = Task.select().where(Task.lane == lane).order_by(Task.position, Task.id)

    # BUILD TASK LIST
    task_list = []

    # ADD TASKS TO TASK LIST
    for task in tasks:
        task_list.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "position": task.position,
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
        "position": task.position,
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

    # DETERMINE NEXT POSITION
    max_position = (
        Task.select(Task.position)
        .where(Task.lane == lane)
        .order_by(Task.position.desc())
        .first()
    )

    # GET NEXT POSITION
    next_position = (max_position.position + 1) if max_position else 0

    # CREATE TASK
    task = Task.create(
        title=title,
        description=description,
        lane=lane,
        position=next_position,
    )

    # SEND RESPONSE
    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "position": task.position,
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
    new_position = data.get("position")

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

        # COMPACT POSITIONS IN THE SOURCE LANE
        old_lane = lane
        old_position = task.position

        # UPDATE TASK POSITION
        Task.update(position=Task.position - 1).where(
            (Task.lane == old_lane) &
            (Task.position > old_position)
        ).execute()

        # DETERMINE INSERTION POSITION IN TARGET LANE
        if new_position is not None:

            # SHIFT TASKS AT AND AFTER THE TARGET POSITION DOWN
            Task.update(position=Task.position + 1).where(
                (Task.lane == target_lane) &
                (Task.position >= new_position)
            ).execute()

            # UPDATE POSITION
            task.position = new_position

        # IF NOT POSITION IS AVAILABLE
        else:

            # APPEND AT END OF TARGET LANE
            max_pos = (
                Task.select(Task.position)
                .where(Task.lane == target_lane)
                .order_by(Task.position.desc())
                .first()
            )

            # UPDATE TASK POSITION
            task.position = (max_pos.position + 1) if max_pos else 0

        # GET LANE FOR TAKS
        task.lane = target_lane

    # IF HAS NO NEW POSITION BUT AN EXISTING POSITION
    elif "position" in data:

        # REORDER WITHIN THE SAME LANE
        old_position = task.position

        # IF GOT NEW POSITION
        if new_position is not None and new_position != old_position:

            # IF POSITION BIGGER THAN OLD ONE
            if new_position > old_position:

                # MOVING DOWN
                Task.update(position=Task.position - 1).where(
                    (Task.lane == lane) &
                    (Task.position > old_position) &
                    (Task.position <= new_position)
                ).execute()

            # IF POSITION ID SMALLER OR SAME AS BEFORE
            else:

                # MOVING UP
                Task.update(position=Task.position + 1).where(
                    (Task.lane == lane) &
                    (Task.position >= new_position) &
                    (Task.position < old_position)
                ).execute()

            # UPDATE TAK POSITION
            task.position = new_position

    # SAVE CHANGES
    task.save()

    # SEND RESPONSE
    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "position": task.position,
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
        "position": task.position,
    }

    # COMPACT POSITIONS IN LANE
    Task.update(position=Task.position - 1).where(
        (Task.lane == lane) &
        (Task.position > task.position)
    ).execute()

    # DELETE TASK
    task.delete_instance()

    # SEND RESPONSE
    return jsonify(deleted_task), 200
