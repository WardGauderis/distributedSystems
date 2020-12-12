from . import bp
from flask import render_template, request
from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES
import requests


# TODO check foutief, login

@bp.app_errorhandler(HTTPException)
def error_handler(error):
	return {'code': error.code, 'description': error.description,
			'error': HTTP_STATUS_CODES.get(error.code, 'Unknown error')}  # TODO


@bp.route('/', methods=['GET'], defaults={'season': 0})
@bp.route('/<int:season>', methods=['GET'])
def index(season):
	stats = requests.get(f'http://nginx/api/stats/top/{season}').json()
	seasons = requests.get('http://nginx/api/crud/seasons').json()
	return render_template('index.html', stats=stats, seasons=seasons, season=season)


@bp.route('/divisions/<int:div>/<int:team>/<int:season>', methods=['GET'])
def divisions(div, team, season):
	print(request.args)
	division = requests.get(f'http://nginx/api/crud/divisions/{div}').json()
	seasons = requests.get(f'http://nginx/api/crud/seasons').json()

	fixtures = requests.get(f'http://nginx/api/stats/fixtures/{div}/{team}/{season}').json()
	table = requests.get(f'http://nginx/api/stats/league_tables/{div}/{season}').json()

	weeks = sorted(set(map(lambda fixture: int(fixture['matchweek']), fixtures)))
	fixtures = {week: [fixture for fixture in fixtures if int(fixture['matchweek']) == week] for week in weeks}

	return render_template('division.html', table=table, fixtures=fixtures, seasons=seasons, division=division,
						   season=season, team=str(team))


@bp.route('/teams/<int:id>', methods=['GET'])
def teams(id):
	return ''
