from flask import Blueprint, Flask

bp = Blueprint('frontend', __name__)

from . import frontend


class Config:
	SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_app() -> Flask:
	app = Flask(__name__)
	app.config.from_object(Config)
	app.register_blueprint(bp)
	from app.general import bp as general
	app.register_blueprint(general)
	return app
