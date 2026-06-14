# IMPORTS
from flask import Blueprint
import src.controllers.lanes as lanes
from src.services.auth_service import require_http_auth

# CREATE BLUEPRINT
lanes_bp = Blueprint("lanes", __name__)

# HOOK: REQUIRE AUTHENTICATION
@lanes_bp.before_request
def authenticate_lane_requests():
    return require_http_auth()

# ROUTE: GET ALL
@lanes_bp.get("/boards/<int:board_id>/lanes")
def get_lanes(board_id):
    return lanes.get_all(board_id)

# ROUTE: GET BY ID
@lanes_bp.get("/boards/<int:board_id>/lanes/<int:lane_id>")
def get_lane_by_id(board_id, lane_id):
    return lanes.get_by_id(board_id, lane_id)

# ROUTE: CREATE
@lanes_bp.post("/boards/<int:board_id>/lanes")
def create_lane(board_id):
    return lanes.create(board_id)

# ROUTE: UPDATE
@lanes_bp.patch("/boards/<int:board_id>/lanes/<int:lane_id>")
def update_lane(board_id, lane_id):
    return lanes.update(board_id, lane_id)

# ROUTE: DELETE
@lanes_bp.delete("/boards/<int:board_id>/lanes/<int:lane_id>")
def delete_lane(board_id, lane_id):
    return lanes.delete(board_id, lane_id)
