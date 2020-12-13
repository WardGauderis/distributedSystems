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
	divisions = requests.get(f'http://nginx/api/crud/divisions').json()
	stats = requests.get(f'http://nginx/api/stats/top/{season}').json()
	seasons = requests.get('http://nginx/api/crud/seasons').json()
	return render_template('index.html', stats=stats, seasons=seasons, season=season, divisions=divisions)


@bp.route('/divisions/<int:div>/<int:team>/<int:season>', methods=['GET'])
def divisions(div, team, season):
	print(request.args)
	divisions = requests.get(f'http://nginx/api/crud/divisions').json()
	division = divisions[div - 1]
	seasons = requests.get(f'http://nginx/api/crud/seasons').json()

	fixtures = requests.get(f'http://nginx/api/stats/fixtures/{div}/{team}/{season}').json()
	table = requests.get(f'http://nginx/api/stats/league_tables/{div}/{season}').json()

	weeks = sorted(set(map(lambda fixture: int(fixture['matchweek']), fixtures)))
	fixtures = {week: [fixture for fixture in fixtures if int(fixture['matchweek']) == week] for week in weeks}

	return render_template('division.html', table=table, fixtures=fixtures, seasons=seasons, division=division,
						   season=season, team=str(team), divisions=divisions)


@bp.route('/teams/<int:id>', methods=['GET'])
def teams(id):
	divisions = requests.get(f'http://nginx/api/crud/divisions').json()
	team = requests.get(f'http://nginx/api/stats/teams/{id}').json()
	try:
		division = divisions[int(team['recent_matches'][0]['division_id']) - 1]['name']
	except:
		division = None
	return render_template('team.html', divisions=divisions, team=team, division=division)


@bp.route('/fixtures/<int:id>', methods=['GET'])
def fixtures(id):
	divisions = requests.get(f'http://nginx/api/crud/divisions').json()
	fixture = requests.get(f'http://nginx/api/stats/fixtures/{id}').json()
	division = divisions[int(fixture['division_id']) - 1]['name']
	return render_template('fixture.html', divisions=divisions, fixture=fixture, division=division)
