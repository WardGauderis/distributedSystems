from . import bp
from flask import render_template
from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES
import requests


def load_user():
	requests.get('http://nginx/api/auth').json()


@bp.app_errorhandler(HTTPException)
def error_handler(error):
	return {'code': error.code, 'description': error.description,
			'error': HTTP_STATUS_CODES.get(error.code, 'Unknown error')}  # TODO


@bp.route('/', methods=['GET'])
def index():
	return render_template('index.html')
