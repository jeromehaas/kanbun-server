# IMPORTS
from flask import Blueprint
import src.controllers.seed as seed

# CREATE BLUEPRINT
seed_bp = Blueprint("seed", __name__)

# ROUTE: CREATE
@seed_bp.post("/seed")
def seed_database():
    return seed.create()
