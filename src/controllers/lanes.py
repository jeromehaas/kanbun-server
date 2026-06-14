# IMPORTS
from flask import jsonify, request
from src.models import Board, Task, Lane
from peewee import fn
from src.realtime import broadcast_board_event, get_board_event_actor_name

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

    # GET ACTOR NAME
    actor_name = get_board_event_actor_name()

    # BROADCAST LANE CREATION
    broadcast_board_event(
        board_id,
        "lane.created",
        {
            "lane_id": lane.id,
            "name": lane.name,
            "position": lane.position,
            "message": f'{ actor_name } created lane { lane.name }',
        },
        request.headers.get("X-Client-Id"),
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

    # SAVE ORIGINAL VALUES FOR REALTIME COPY
    original_name = lane.name
    original_position = lane.position

    # GET DB HANDLER
    db = Lane._meta.database

    # GET DATA FROM BODY
    data = request.get_json() or {}
    lane_name = data.get("name")
    position = data.get("position")

    # UPDATE NAME IN MEMORY IF PROVIDED
    if lane_name is not None:

        # GET EXISTING LANE WITH SAME NAME (SCOPED TO BOARD, EXCLUDING SELF)
        existing_lane = Lane.get_or_none(
            (Lane.name == lane_name) &
            (Lane.board == board) &
            (Lane.id != lane_id)
        )

        # CHECK FOR EXISTING LANE
        if existing_lane:
            return jsonify({
                "ERROR": "A LANE WITH THIS NAME ALREADY EXISTS"
            }), 400

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

    # BROADCAST LANE UPDATE
    lane_was_renamed = lane.name != original_name
    lane_was_moved = lane.position != original_position
    actor_name = get_board_event_actor_name()

    # DEFINE REALTIME MESSAGE DEPENDING ON EVENT
    if lane_was_renamed and lane_was_moved:
        realtime_message = f'{ actor_name } renamed lane { original_name } to { lane.name } and moved it'
    elif lane_was_renamed:
        realtime_message = f'{ actor_name } renamed lane { original_name } to { lane.name }'
    elif lane_was_moved:
        realtime_message = f'{ actor_name } moved lane { lane.name }'
    else:
        realtime_message = f'{ actor_name } updated lane { lane.name }'

    # BROADCAST BOARD EVENT
    broadcast_board_event(
        board_id,
        "lane.updated",
        {
            "lane_id": lane.id,
            "name": lane.name,
            "position": lane.position,
            "message": realtime_message,
        },
        request.headers.get("X-Client-Id"),
    )

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

    # GET ACTOR NAME
    actor_name = get_board_event_actor_name()

    # BROADCAST LANE DELETION
    broadcast_board_event(
        board_id,
        "lane.deleted",
        {
            **deleted_lane,
            "message": f'{ actor_name } deleted lane { deleted_lane["name"] }',
        },
        request.headers.get("X-Client-Id"),
    )

    # SEND RESPONSE
    return jsonify(
        deleted_lane
    ), 200
