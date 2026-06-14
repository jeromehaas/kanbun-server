# IMPORTS
from src.models import db, User, Board, Task, Lane

# DEFINE MODELS
models = [User, Board, Lane, Task]

# FUNCTION: ENSURE TABLES
def ensure_tables():

    # CREATE TABLES
    with db:
        db.create_tables(models)

# FUNCTION: RESET TABLES
def reset_tables():

    # DROP AND RECREATE ALL TABLES
    with db:
        db.drop_tables(models, safe=True)
        db.create_tables(models, safe=True)
