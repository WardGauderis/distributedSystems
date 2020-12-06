from os import environ

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Config:
	SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URI")
	SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_app() -> Flask:
	app = Flask(__name__)
	app.config.from_object(Config)
	db.init_app(app)
	from stats import bp
	app.register_blueprint(bp)
	return app


app = create_app()

if __name__ == '__main__':
	app.run(host='0.0.0.0')
