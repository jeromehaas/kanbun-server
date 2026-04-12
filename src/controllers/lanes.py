# IMPORTS
from flask import jsonify, request
from src.models import Board, Task, Lane

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

    # ADD LANES TO LANE LIST
    for lane in board.lanes.order_by(Lane.position):
        lane_list.append({
            "id": lane.id,
            "name": lane.name,
            "position": lane.position,
        })

    # SEND RESPONSE
    return jsonify(
        lane_list,
    ), 200

# FUNCTION: GET BY ID
def get_by_id(board_id, lane_id):

    # GET BOARD
    board = Board.get_or_none(Board.id == board_id);

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

    # SEND RESPONSE
    return jsonify({
        "id": lane.id,
        "name": lane.name,
        "position": lane.position,
    }), 200

# FUNCTION: CREATE
def create(board_id):

    # GET BOARD
    board = Board.get_or_none(board_id)

    # CHECK FOR BOARD
    if board is None:
        return jsonify({
            "ERROR": "NO BOARD WAS FOUND"
        }), 404

    # GET DATA FROM BODY
    data = request.get_json() or {}
    name = data.get("name")
    position = data.get("position")

    # CREATE LANE
    lane = Lane.create(
        board_id=board_id,
        name=name,
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

    # GET DATA FROM BODY
    data = request.get_json() or {}
    name = data.get("name")
    position = data.get("position")

    # UPDATE NAME IF PROVIDED
    if "name" in data:
        lane.name = name

    # UPDATE POSITION IF PROVIDED
    if "position" in data:
        lane.position = position

    # SAVE CHANGES
    lane.save()

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
    return jsonify(deleted_lane), 200
