# IMPORTS
import os
from dotenv import load_dotenv
from src.models import db

# FUNCTION: INIT DATABASE
def init_database():

    # LOAD DOTENV
    load_dotenv()

    # GET DB CREDENTIALS
    database_name = os.getenv("DATABASE_DB_NAME")
    database_user = os.getenv("DATABASE_USER")
    database_password = os.getenv("DATABASE_PASSWORD")
    database_host = os.getenv("DATABASE_HOST")
    database_port = os.getenv("DATABASE_PORT")

    # CHECK ALL CREDENTIALS
    if not all([database_name, database_user, database_password, database_host, database_port]):
        raise RuntimeError("DATABASE ENVIRONMENT VARIABLES ARE MISSING OR INVALID.")

    # INIT DB
    db.init(
        database_name,
        user=database_user,
        password=database_password,
        host=database_host,
        port=int(database_port),
    )

# FUNCTION: OPEN DB CONNECTION
def open_db_connection():

    # IS DB IS CLOSED, OPEN IT
    if db.is_closed():
        db.connect()

# FUNCTION: CLOSE DB CONNECTION
def close_db_connection(exc=None):

    # IF DB IS NOT CLOSED, THEN CLOSE IT
    if not db.is_closed():
        db.close()

# FUNCTION: REGISTER DB HOOKS
def register_db_hooks(app):

    # ON LOAD, SETUP BEFORE AND TEARDOWN HOOKS
    app.before_request(open_db_connection)
    app.teardown_request(close_db_connection)