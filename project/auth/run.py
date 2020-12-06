from os import environ

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Config:
	SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URI")
	SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_app() -> Flask:
	app = Flask(__name__)
	app.config.from_object(Config)
	db.init_app(app)
	return app


app = create_app()


@app.route('/', methods=['GET'])
def temp():
	return "auth"


if __name__ == '__main__':
	app.run(host='0.0.0.0')
