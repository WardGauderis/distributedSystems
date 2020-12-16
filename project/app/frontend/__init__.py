from flask import Blueprint, Flask
from flask_login import LoginManager

bp = Blueprint('frontend', __name__)
login = LoginManager()
login.login_view = 'frontend.login'
login.login_message_category = 'danger'

from . import frontend


class Config:
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SECRET_KEY = 'LiefhebbersVoetbalLiga'
	WTF_CSRF_ENABLED = False

def create_app() -> Flask:
	app = Flask(__name__)
	app.config.from_object(Config)
	login.init_app(app)
	app.register_blueprint(bp)
	return app
