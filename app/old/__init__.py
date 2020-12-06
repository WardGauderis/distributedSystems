from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import environ

db = SQLAlchemy()

class Config:
	SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URI")
	SQLALCHEMY_TRACK_MODIFICATIONS = False

def create_app() -> Flask:
	app = Flask(__name__)
	app.config.from_object(Config)
	db.init_app(app)
	return app