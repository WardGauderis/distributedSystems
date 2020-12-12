from base64 import b64decode

import jwt
from flask import request, abort, current_app
import requests

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
		method = request.headers['X-Original-Method']
		uri = request.headers['X-Original-Uri']
		if method == 'GET' and not uri.startswith('/api/crud/users/'):
			return ''

		value = request.headers['Authorization']
		scheme, token = value.split(None, 1)
		data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
		user = User.query.get(data['id'])

		admin = user.is_admin
		super_admin = user.is_super_admin
		allowed = False

		if '/admins/' in uri:
			allowed = super_admin
		elif admin or super_admin:
			allowed = True
		elif uri.startswith('/api/crud/matches/') and method == 'PATCH':  # TODO check
			allowed = int(requests.get('http://crud:5000' + uri[9:]).json()['home_team_id']) == user.team_id
		elif uri.startswith('/api/crud/clubs/') and method == 'PUT':
			allowed = int(requests.get('http://crud:5000' + uri[9:]).json()['stam_number']) == user.team_id

		if allowed:
			return ''
		else:
			abort(403)
	except:
		raise
		pass
	abort(401)


@bp.route('/error', methods=['GET'])
def error():
	abort(int(request.headers['code']))
