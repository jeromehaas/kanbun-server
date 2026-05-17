# IMPORTS
from flask import jsonify, request
from src.models import Board, Task, Lane
from peewee import fn

# FUNCTION: GET ALL
def get_all(board_id):

    # GET BOARD
    board = Board.get_or_none(Board.id == board_id)

    # CHECK FOR BOARD
    if board is None:
        return jsonify({
            "ERROR": "NO BOARD WAS FOUND"
        }), 404

    # DEFINE LANE LIST
    lane_list = []

    # LOOP OVER LANES
    for lane in board.lanes.order_by(Lane.position):

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

        # ADD LANES TO LANE LIST
        lane_list.append({
            "id": lane.id,
            "name": lane.name,
            "position": lane.position,
            "tasks": task_list,
        })

    # SEND RESPONSE
    return jsonify(
        lane_list,
    ), 200

# FUNCTION: GET BY ID
def get_by_id(board_id, lane_id):

    # GET BOARD
    board = Board.get_or_none(Board.id == board_id)

    # CHECK FOR BOARD
    if board is None:
        return jsonify({
            "ERROR": "NO BOARD WAS FOUND"
        }), 404

    # GET LANE
    lane = Lane.get_or_none((Lane.id == lane_id) & (Lane.board == board))

    # CHECK FOR LANE
    if lane is None:
        return jsonify({
            "ERROR": "NO LANE WAS FOUND"
        }), 404

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

    # SEND RESPONSE
    return jsonify({
        "id": lane.id,
        "name": lane.name,
        "position": lane.position,
        "tasks": task_list,
    }), 200

# FUNCTION: CREATE
def create(board_id):

    # GET BOARD
    board = Board.get_or_none(Board.id == board_id)

    # CHECK FOR BOARD
    if board is None:
        return jsonify({
            "ERROR": "NO BOARD WAS FOUND"
        }), 404

    # GET DATA FROM BODY
    data = request.get_json() or {}
    lane_name = data.get("name")

    # CHECK FOR NAME
    if not lane_name:
        return jsonify({
            "ERROR": "LANE NAME IS REQUIRED"
        }), 400

    # CHECK FOR EXISTING LANE WITH SAME NAME (SCOPED TO BOARD)
    existing_lane = Lane.get_or_none((Lane.name == lane_name) & (Lane.board == board))
    if existing_lane:
        return jsonify({
            "ERROR": "A LANE WITH THIS NAME ALREADY EXISTS"
        }), 400

    # GET HIGHEST POSITION OF LANES
    highest_position = (
        Lane
        .select(fn.Max(Lane.position))
        .where(Lane.board == board)
        .scalar()
    )

    # DEFINE POSITION
    position = (highest_position or 0) + 1

    # CREATE LANE
    lane = Lane.create(
        board_id=board_id,
        name=lane_name,
        position=position,
    )

    # SEND RESPONSE
    return jsonify({
        "id": lane.id,
        "name": lane.name,
        "position": lane.position,
    }), 201

# FUNCTION: UPDATE
def update(board_id, lane_id):

    # GET BOARD
    board = Board.get_or_none(Board.id == board_id)

    # CHECK FOR BOARD
    if board is None:
        return jsonify({
            "ERROR": "NO BOARD WAS FOUND"
        }), 404

    # GET LANE
    lane = Lane.get_or_none(
        (Lane.id == lane_id) &
        (Lane.board == board)
    )

    # CHECK FOR LANE
    if lane is None:
        return jsonify({
            "ERROR": "NO LANE WAS FOUND"
        }), 404

    # GET DB HANDLER
    db = Lane._meta.database

    # GET DATA FROM BODY
    data = request.get_json() or {}
    lane_name = data.get("name")
    position = data.get("position")

    # UPDATE NAME IN MEMORY IF PROVIDED
    if lane_name is not None:
        # CHECK FOR EXISTING LANE WITH SAME NAME (SCOPED TO BOARD, EXCLUDING SELF)
        existing_lane = Lane.get_or_none(
            (Lane.name == lane_name) &
            (Lane.board == board) &
            (Lane.id != lane_id)
        )
        if existing_lane:
            return jsonify({
                "ERROR": "A LANE WITH THIS NAME ALREADY EXISTS"
            }), 400
        lane.name = lane_name

        # UPDATE NAME IN MEMORY IF PROVIDED
        lane.name = lane_name

    # HANDLE POSITION UPDATE
    if position is not None:

        # VALIDATE TYPE
        if not isinstance(position, int):
            return jsonify({
                "ERROR": "POSITION MUST BE AN INTEGER"
            }), 400

        # GET NEW AND OLD POSITION
        new_position = position
        old_position = lane.position

        # VALIDATE VALUE
        if new_position < 1:
            return jsonify({
                "ERROR": "POSITION MUST BE GREATER THAN OR EQUAL TO 1"
            }), 400

        # ONLY REORDER IF POSITION CHANGED
        if new_position != old_position:

            # GET HIGHEST POSITION OF LANES
            highest_position = (
                Lane
                .select(fn.MAX(Lane.position))
                .where(Lane.board == board)
                .scalar()
            ) or 0

            # CLAMP TO LAST VALID POSITION
            if new_position > highest_position:
                new_position = highest_position

            # START BULK OPERATION
            with db.atomic():

                # MOVE CURRENT LANE TO A TEMPORARY FREE POSITION
                temp_position = highest_position + 1
                lane.position = temp_position
                lane.save(only=[Lane.position])

                # IF NEW POSITION IS SMALLER THAN OLD POSITION
                if new_position < old_position:

                    # UPDATE LANE POSITIONS
                    (Lane
                     .update({Lane.position: Lane.position + 1})
                     .where(
                         (Lane.board == board) &
                         (Lane.id != lane.id) &
                         (Lane.position >= new_position) &
                         (Lane.position < old_position)
                     )
                     .execute())

                # IF NEW POSITION IS BIGGER THAN OLD POSITION
                else:

                    # UPDATE LANE POSITIONS
                    (Lane
                     .update({Lane.position: Lane.position - 1})
                     .where(
                         (Lane.board == board) &
                         (Lane.id != lane.id) &
                         (Lane.position > old_position) &
                         (Lane.position <= new_position)
                     )
                     .execute())

                # FINAL POSITION + POSSIBLE NAME CHANGE
                lane.position = new_position
                lane.save(only=lane.dirty_fields)

        # IF POSITIONS HAVE NOT CHANGED
        else:

            # CHECK IF DIRTY FIELDS ARE AVAILABLE
            if lane.dirty_fields:

                # SAVE DIRTY FIELDS
                lane.save(only=lane.dirty_fields)

    # IF POSITION IS NOT AVAILABLE
    else:

        # CHECK IF DIRTY FIELDS ARE AVAILABLE
        if lane.dirty_fields:

            # SAVE DIRTY FIELDS
            lane.save(only=lane.dirty_fields)

    # SEND RESPONSE
    return jsonify({
        "id": lane.id,
        "name": lane.name,
        "position": lane.position
    }), 200

# FUNCTION: DELETE
def delete(board_id, lane_id):

    # GET BOARD
    board = Board.get_or_none(Board.id == board_id)

    # CHECK FOR BOARD
    if board is None:
        return jsonify({
            "ERROR": "BOARD WAS NOT FOUND"
        }), 404

    # GET LANE
    lane = Lane.get_or_none(
        (Lane.id == lane_id) &
        (Lane.board == board)
    )

    # CHECK FOR LANE
    if lane is None:
        return jsonify({
            "ERROR": "LANE WAS NOT FOUND"
        }), 404

    # SAVE DELETED LANE
    deleted_lane = {
        "id": lane.id,
        "board_id": lane.board.id,
        "name": lane.name,
        "position": lane.position,
    }

    # DELETE LANE
    lane.delete_instance(recursive=True)

    # SEND RESPONSE
    return jsonify(
        deleted_lane
    ), 200
