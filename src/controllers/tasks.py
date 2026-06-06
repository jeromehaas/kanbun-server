# IMPORTS
from flask import jsonify, request
from src.models import Board, Task, Lane
from src.realtime import broadcast_board_event

# FUNCTION: NORMALIZE TASK POSITIONS
def normalize_task_positions(lane):

    # GET TASKS IN STABLE ORDER
    tasks = list(
        Task.select()
        .where(Task.lane == lane)
        .order_by(Task.position, Task.id)
    )

    # REWRITE POSITIONS TO A COMPACT ZERO-BASED SEQUENCE
    for index, lane_task in enumerate(tasks):
        if lane_task.position != index:
            lane_task.position = index
            lane_task.save(only=[Task.position])

    # RETURN ORDERED TASKS
    return tasks

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

    # NORMALIZE EXISTING TASK POSITIONS BEFORE APPENDING
    normalize_task_positions(lane)

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

    # BROADCAST TASK CREATION
    broadcast_board_event(
        board_id,
        "task.created",
        {
            "task_id": task.id,
            "lane_id": lane.id,
            "position": task.position,
            "title": task.title,
        },
        request.headers.get("X-Client-Id"),
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

    # NORMALIZE SOURCE LANE POSITIONS BEFORE REORDERING
    normalize_task_positions(lane)
    task = Task.get_by_id(task.id)
    original_lane_id = task.lane.id
    original_position = task.position

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

        # NORMALIZE TARGET LANE BEFORE INSERTING INTO IT
        if target_lane.id != lane.id:
            normalize_task_positions(target_lane)

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

            # CLAMP THE TARGET POSITION TO THE LANE BOUNDS
            target_task_count = Task.select().where(Task.lane == target_lane).count()
            new_position = max(0, min(new_position, target_task_count))

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

            # CLAMP THE TARGET POSITION TO THE LANE BOUNDS
            lane_task_count = Task.select().where(Task.lane == lane).count()
            new_position = max(0, min(new_position, lane_task_count - 1))

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

    # DETECT CARD MOVES FOR REALTIME UPDATES
    task_was_moved = (
        task.lane.id != original_lane_id or
        task.position != original_position
    )

    # BROADCAST TASK UPDATE
    broadcast_board_event(
        board_id,
        "task.moved" if task_was_moved else "task.updated",
        {
            "task_id": task.id,
            "title": task.title,
            "from_lane_id": original_lane_id,
            "to_lane_id": task.lane.id,
            "from_position": original_position,
            "to_position": task.position,
            "message": (
                f'Task "{task.title}" moved to a new position'
                if task_was_moved
                else f'Task "{task.title}" was updated'
            ),
        },
        request.headers.get("X-Client-Id"),
    )

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

    # NORMALIZE POSITIONS BEFORE REMOVING A TASK FROM THE LANE
    normalize_task_positions(lane)
    task = Task.get_by_id(task.id)

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

    # BROADCAST TASK DELETION
    broadcast_board_event(
        board_id,
        "task.deleted",
        {
            "task_id": deleted_task["id"],
            "lane_id": lane.id,
            "title": deleted_task["title"],
            "position": deleted_task["position"],
            "message": f'Task "{deleted_task["title"]}" was deleted',
        },
        request.headers.get("X-Client-Id"),
    )

    # SEND RESPONSE
    return jsonify(deleted_task), 200
