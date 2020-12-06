from flask import Blueprint, request, jsonify
from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES

bp = Blueprint('general', __name__)


def json_error():
	return (
			request.accept_mimetypes['application/json']
			>= request.accept_mimetypes['text/html']
	)


def error_message(status_code):
	return HTTP_STATUS_CODES.get(status_code, 'Unknown error');


@bp.app_errorhandler(HTTPException)
def error_handler(error):
	if json_error():
		payload = {'code': error.code, 'error': error_message(error.code), 'description': error.description}
		response = jsonify(payload)
		response.status_code = error.code
		return response
	else:
		return "DIT WORDT EEN MOOIE PAGINA"  # TODO
