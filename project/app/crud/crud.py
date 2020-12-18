from . import bp, db
from app.general.models import *
from flask import request, jsonify, abort
from sqlalchemy import exc
from psycopg2 import errorcodes


def handle_error(e, model):
	code = e.orig.pgcode
	if code == errorcodes.UNIQUE_VIOLATION:
		if model == 'match':
			message = str(e.orig)
			if 'match_home_team_id_date_key' in message or 'match_away_team_id_date_key' in message:
				abort(409, f'Not all teams are free to participate in this match this day.')
			if 'match_referee_id_date_key' in message:
				abort(409, f'Referee is not free to participate in this match this day.')
		abort(409, f'This {model} already exists.')
	elif code == errorcodes.NOT_NULL_VIOLATION:
		abort(400, f'Not all required information was provided.')
	elif code == errorcodes.INVALID_TEXT_REPRESENTATION:
		abort(400, f'Not all information was correctly formatted.')
	elif code == errorcodes.FOREIGN_KEY_VIOLATION:
		abort(409, f'Could not find the referenced id/stam_number.')
	elif code == errorcodes.STRING_DATA_RIGHT_TRUNCATION:
		abort(400, f'String value is too long.')
	elif code == errorcodes.CHECK_VIOLATION:
		abort(409, f'This information does not represent a logically correct {model}.')
	elif code == errorcodes.INVALID_DATETIME_FORMAT:
		abort(400, f'Date/Time was not correctly formatted.')
	else:
		abort(500, str(e.orig) + ' ' + str(type(e.orig)))


@bp.route('/clubs', methods=['GET', 'POST'])
def clubs():
	if request.method == 'GET':
		clubs = [club.serialize() for club in Club.query.order_by(Club.name).all()]
		return jsonify(clubs)
	elif request.method == 'POST':
		club = Club()
		try:
			club.deserialize(request.get_json(force=True) or {})
			db.session.add(club)
			db.session.commit()
			return jsonify({'stam_number': club.stam_number})
		except exc.StatementError as e:
			handle_error(e, 'club')


@bp.route('/clubs/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def club(id):
	club = Club.query.get(id)
	if not club: abort(404)

	if request.method == 'GET':
		return jsonify(club.serialize())
	elif request.method == 'DELETE':
		db.session.delete(club)
		db.session.commit()
		return ''
	elif request.method == 'PUT':
		try:
			club.deserialize(request.get_json(force=True) or {})
			db.session.add(club)
			db.session.commit()
			return ''
		except exc.StatementError as e:
			handle_error(e, 'club')


@bp.route('/teams', methods=['GET', 'POST'])
def teams():
	if request.method == 'GET':
		teams = [team.serialize() for team in
				 Team.query.join(Club, Club.stam_number == Team.stam_number).order_by(Club.name, Team.suffix).all()]
		return jsonify(teams)
	elif request.method == 'POST':
		team = Team()
		try:
			team.deserialize(request.get_json(force=True) or {})
			db.session.add(team)
			db.session.commit()
			return jsonify({'id': team.id})
		except exc.StatementError as e:
			handle_error(e, 'team')


@bp.route('/teams/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def team(id):
	team = Team.query.get(id)
	if not team: abort(404)

	if request.method == 'GET':
		return jsonify(team.serialize())
	elif request.method == 'DELETE':
		db.session.delete(team)
		db.session.commit()
		return ''
	elif request.method == 'PUT':
		try:
			team.deserialize(request.get_json(force=True) or {})
			db.session.add(team)
			db.session.commit()
			return ''
		except exc.StatementError as e:
			handle_error(e, 'team')


@bp.route('/divisions', methods=['GET', 'POST'])
def divisions():
	if request.method == 'GET':
		divisions = [division.serialize() for division in Division.query.order_by(Division.name).all()]
		return jsonify(divisions)
	elif request.method == 'POST':
		division = Division()
		try:
			division.deserialize(request.get_json(force=True) or {})
			db.session.add(division)
			db.session.commit()
			return jsonify({'id': division.id})
		except exc.StatementError as e:
			handle_error(e, 'division')


@bp.route('/divisions/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def division(id):
	division = Division.query.get(id)
	if not division: abort(404)

	if request.method == 'GET':
		return jsonify(division.serialize())
	elif request.method == 'DELETE':
		db.session.delete(division)
		db.session.commit()
		return ''
	elif request.method == 'PUT':
		try:
			division.deserialize(request.get_json(force=True) or {})
			db.session.add(division)
			db.session.commit()
			return ''
		except exc.StatementError as e:
			handle_error(e, 'division')


@bp.route('/matches', methods=['GET', 'POST'])
def matches():
	if request.method == 'GET':
		try:
			matches = Match.query.order_by(Match.date, Match.time, Match.id)
			if 'season' in request.args and request.args['season'] != '0':
				a, b = get_season_start_and_end(int(request.args['season']))
				matches = matches.filter(db.and_(Match.date >= a, Match.date <= b))
			if 'division_id' in request.args and request.args['division_id'] != '0':
				matches = matches.filter(Match.division_id == int(request.args['division_id']))
			if 'team_id' in request.args:
				matches = matches.filter(Match.home_team_id == int(request.args['team_id']))
			matches = [match.serialize() for match in matches.all()]
			return jsonify(matches)
		except:
			abort(400)
	elif request.method == 'POST':
		match = Match()
		try:
			match.deserialize(request.get_json(force=True) or {})
			db.session.add(match)
			db.session.commit()
			return jsonify({'id': match.id})
		except exc.StatementError as e:
			handle_error(e, 'match')


@bp.route('/matches/<int:id>', methods=['GET', 'PUT', 'DELETE', 'PATCH'])
def match(id):
	match = Match.query.get(id)
	if not match: abort(404)

	if request.method == 'GET':
		return jsonify(match.serialize())
	elif request.method == 'DELETE':
		db.session.delete(match)
		db.session.commit()
		return ''
	elif request.method == 'PUT':
		try:
			match.deserialize(request.get_json(force=True) or {})
			db.session.add(match)
			db.session.commit()
			return ''
		except exc.StatementError as e:
			handle_error(e, 'match')
	elif request.method == 'PATCH':
		try:
			json = request.get_json(force=True) or {}
			if 'goals_home_team' in json:
				match.goals_home_team = json.get('goals_home_team')
			if 'goals_away_team' in json:
				match.goals_away_team = json.get('goals_away_team')
			db.session.commit()
			return ''
		except exc.StatementError as e:
			handle_error(e, 'match')


@bp.route('/referees', methods=['GET', 'POST'])
def referees():
	if request.method == 'GET':
		referees = [referee.serialize() for referee in Referee.query.order_by(Referee.first_name, Referee.last_name).all()]
		return jsonify(referees)
	elif request.method == 'POST':
		referee = Referee()
		try:
			referee.deserialize(request.get_json(force=True) or {})
			db.session.add(referee)
			db.session.commit()
			return jsonify({'id': referee.id})
		except exc.StatementError as e:
			handle_error(e, 'referee')


@bp.route('/referees/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def referee(id):
	referee = Referee.query.get(id)
	if not referee: abort(404)

	if request.method == 'GET':
		return jsonify(referee.serialize())
	elif request.method == 'DELETE':
		db.session.delete(referee)
		db.session.commit()
		return ''
	elif request.method == 'PUT':
		try:
			referee.deserialize(request.get_json(force=True) or {})
			db.session.add(referee)
			db.session.commit()
			return ''
		except exc.StatementError as e:
			handle_error(e, 'referee')


@bp.route('/users', methods=['GET', 'POST'])
def users():
	if request.method == 'GET':
		users = [user.serialize() for user in User.query.order_by(User.username).all()]
		return jsonify(users)
	elif request.method == 'POST':
		user = User()
		try:
			user.deserialize(request.get_json(force=True) or {})
			db.session.add(user)
			db.session.commit()
			return jsonify({'id': user.id})
		except exc.StatementError as e:
			handle_error(e, 'user')


@bp.route('/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def user(id):
	user = User.query.get(id)
	if not user: abort(404)

	if request.method == 'GET':
		return jsonify(user.serialize())
	elif request.method == 'DELETE':
		db.session.delete(user)
		db.session.commit()
		return ''
	elif request.method == 'PUT':
		try:
			user.deserialize(request.get_json(force=True) or {})
			db.session.add(user)
			db.session.commit()
			return ''
		except exc.StatementError as e:
			handle_error(e, 'user')


@bp.route('/admins/<int:id>', methods=['POST', 'DELETE'])
def admins(id):
	user = User.query.get(id)
	if not user: abort(404)
	if request.method == 'POST':
		user.is_admin = True
	elif request.method == 'DELETE':
		user.is_admin = False
	db.session.commit()
	return ''


@bp.route('/seasons', methods=['GET'])
def seasons():
	try:
		first = Match.query.order_by(Match.date).limit(1).one_or_none().date
		last = Match.query.order_by(Match.date.desc()).limit(1).one_or_none().date
		first = get_season(first)
		last = get_season(last)

		return jsonify([i for i in range(first, last + 1)])
	except:
		return jsonify([])
