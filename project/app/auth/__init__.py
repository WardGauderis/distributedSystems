from os import environ

from flask import Blueprint, Flask
from flask_sqlalchemy import SQLAlchemy

bp = Blueprint('auth', __name__)

from . import auth

db = SQLAlchemy()


class Config:
	SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URI")
	SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_app() -> Flask:
	app = Flask(__name__)
	app.config.from_object(Config)
	db.init_app(app)
	app.register_blueprint(bp)
	from app.general import bp as general
	app.register_blueprint(general)
	return app
