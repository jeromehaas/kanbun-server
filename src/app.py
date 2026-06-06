# IMPORTS
from flask import Flask
from src.database import init_database, ensure_tables, register_db_hooks
from src.realtime import init_realtime
from src.routes import register_routes

# SETUP APP
app = Flask(__name__)

# SETUP DB
init_database()
ensure_tables()
init_realtime(app)
register_db_hooks(app)
register_routes(app)
