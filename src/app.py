# IMPORTS
from flask import Flask
from src.database import init_database, ensure_tables, register_db_hooks
from src.routes import register_routes

# SETUP APP
app = Flask(__name__)

# SETUP DB
init_database()
ensure_tables()
register_db_hooks(app)
register_routes(app)

