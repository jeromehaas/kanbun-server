# IMPORTS
from .auth import auth_bp
from .tasks import tasks_bp
from .boards import boards_bp
from .lanes import lanes_bp
from .seed import seed_bp

# FUNCTION: REGISTER ROUTES
def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(boards_bp)
    app.register_blueprint(lanes_bp)
    app.register_blueprint(seed_bp)
