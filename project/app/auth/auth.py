from base64 import b64decode

import jwt
from flask import request, abort, current_app

from app.general.models import User
from . import bp


@bp.route('/', methods=['POST'])
def login():
	try:
		value = request.headers['Authorization']
		scheme, credentials = value.split(None, 1)
		username, password = b64decode(credentials).decode('utf-8').split(':', 1)
		user = User.query.filter_by(username=username).one_or_none()
		if user and user.check_password(password):
			token = user.get_token()
			return {'token': token}, 200
	except:
		pass
	abort(401)


@bp.route('/check_auth', methods=['GET'])
def authorize():
	try:
		value = request.headers['Authorization']
		scheme, token = value.split(None, 1)

		data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
		user = User.query.get(data['id'])
		if user is not None:
			uri = request.headers['X-Original-Uri']
			if uri == '/api/crud' and not user.team:	#TODO checks
				abort(403)
			return '', 200
	except:
		raise
		pass
	abort(401)


@bp.route('/error', methods=['GET'])
def error():
	abort(int(request.headers['code']))
