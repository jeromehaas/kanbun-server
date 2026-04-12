# IMPORTS
from flask import Blueprint
import src.controllers.boards as boards

# CREATE BLUEPRINT
boards_bp = Blueprint("boards", __name__)

# ROUTE: GET ALL
@boards_bp.get("/boards")
def get_boards():
    return boards.get_all()

# ROUTE: GET BY ID
@boards_bp.get("/boards/<int:board_id>")
def get_board_by_id(board_id):
    return boards.get_by_id(board_id)

# ROUTE: CREATE
@boards_bp.post("/boards")
def create_board():
    return boards.create()

# ROUTE: UPDATE
@boards_bp.patch("/boards/<int:board_id>")
def update_board(board_id):
    return boards.update(board_id)

# ROUTE: DELETE BY ID
@boards_bp.delete("/boards/<int:board_id>")
def delete_board(board_id):
    return boards.delete(board_id)
