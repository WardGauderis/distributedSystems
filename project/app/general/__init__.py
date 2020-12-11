from flask import Blueprint, jsonify
from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES

bp = Blueprint('general', __name__)


def error_message(status_code):
	return HTTP_STATUS_CODES.get(status_code, 'Unknown error')


@bp.app_errorhandler(HTTPException)
def error_handler(error):
	payload = {'code': error.code, 'description': error.description,
			   'error': HTTP_STATUS_CODES.get(error.code, 'Unknown error')}
	response = jsonify(payload)
	response.status_code = error.code
	return response
