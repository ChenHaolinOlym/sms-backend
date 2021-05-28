from flask_smorest import Api

from .schemas import ma

from .info import info_blp
from .events import event_blp
from .pieces import piece_blp
from .files import file_blp

api = Api()

def register_blueprints() -> None:
    """Register all blueprints"""
    api.register_blueprint(info_blp)
    api.register_blueprint(event_blp)
    api.register_blueprint(piece_blp)
    api.register_blueprint(file_blp)

