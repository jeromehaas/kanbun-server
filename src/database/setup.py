# IMPORTS
from src.models import db, Board, Task, Lane

# FUNCTION: ENSURE TABLES
def ensure_tables():

    # IF DB CONNECTION IS SETUP, CREATE TABLES
    with db:
        db.create_tables([Board, Lane, Task])