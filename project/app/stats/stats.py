from datetime import date, datetime, timedelta

import requests
from flask import jsonify, abort

from app.general.models import Division, Match, Team, get_season, get_season_start_and_end
from . import bp


def weather(datum, time, location):
	try:
		json = requests.get('http://api.positionstack.com/v1/forward', {
			'access_key': 'f21de7a509fc77d30142b724bc3f53ef',
			'query': location,
			'country': 'BE',
			'region': 'Antwerp',
			'limit': 1,
		}).json()
		lat = json['data'][0]['latitude']
		lon = json['data'][0]['longitude']
		json = requests.get('http://api.openweathermap.org/data/2.5/onecall', {
			'appid': '7cad07efa2c3ba1124667a8fd6c75483',
			'lat': lat,
			'lon': lon,
			'exclude': 'current,minutely,hourly,alerts',
			'units': 'metric'
		}).json()
		weather = json['daily'][(datum - date.today()).days]
		return {
			'temp_max': weather['temp']['max'],
			'temp_min': weather['temp']['min'],
			'description': weather['weather'][0]['description'],
			'icon': weather['weather'][0]['icon'],
			'humidity': weather['humidity'],
			'feels_like': weather['feels_like']['day']
		}
	except:
		return 'Weather/Geolocation service error. Please refresh.'


@bp.route('/league_tables/<int:div>/<int:season>', methods=['GET'])
def league_table(div, season):
	division = Division.query.get(div) or abort(404)
	a = {}
	a.update()
	try:
		a, b = get_season_start_and_end(season)
		teams = division.teams(a, b)
		result = [{
			'team': team.serialize(),
			'played': team.played(division, a, b),
			'won': team.won(division, a, b),
			'drawn': team.drawn(division, a, b),
			'lost': team.lost(division, a, b),
			'GF': team.gf(division, a, b),
			'GA': team.ga(division, a, b),
			'GD': team.gd(division, a, b),
			'points': team.points(division, a, b)
		} for team in teams]
		result.sort(key=lambda x: x['points'], reverse=True)
		for i in range(len(result)):
			result[i]['pos'] = i + 1
		return jsonify(result)
	except:
		abort(400)


@bp.route('/fixtures/<int:div>/<int:team>/<int:season>', methods=['GET'])
def fixtures(div, team, season):
	try:
		a, b = get_season_start_and_end(season, False)
		query = Match.query.filter(Match.division_id == div).filter(Match.date >= a, Match.date < b)
		if team:
			query = query.filter(Match.home_team_id == team or Match.away_team_id == team)
		matches = query.order_by(Match.date, Match.time).all()
		return jsonify([match.serialize() for match in matches])
	except:
		abort(400)


@bp.route('/top/<int:season>', methods=['GET'])
def top(season):
	try:
		a, b = get_season_start_and_end(season)
		result = []
		for division in Division.divisions_in_season(a, b):
			attack, gf = division.best_attack(a, b)
			defense, ga = division.best_defence(a, b)
			sheets, count = division.most_clean_sheets(a, b)
			result.append({
				**division.serialize(), **{
					'best_attack': {**attack.serialize(), **{'GF': gf}},
					'best_defence': {**defense.serialize(), **{'GA': ga}},
					'most_clean_sheets': {**sheets.serialize(), **{'count': count}}
				}
			})
		return jsonify(result)
	except:
		raise
		abort(400)


@bp.route('/fixtures/<int:id>', methods=['GET'])
def fixture(id):
	match = Match.query.get(id)
	if not match:
		abort(404)
	result = match.serialize()
	result['location'] = match.home_team.club.location()
	if (match.date > date.today() or (
			match.date == date.today() and match.time > datetime.now().time())) and match.goals_home_team is None:
		a, b = get_season_start_and_end(get_season(match.date))
		b = min(b, match.date)
		count, home_team_wins, away_team_wins = match.history(a, b)
		result['previous_games'] = count
		result['home_team_wins'] = home_team_wins
		result['away_team_wins'] = away_team_wins

		result['recent_matches'] = []
		for recent_match in match.recent(a, b):
			result['recent_matches'].append(recent_match.serialize())

		result['recent_matches_home_team'] = []
		for home_team_match in match.home_team.recent(b, 5):
			result['recent_matches_home_team'].append({
				'id': home_team_match.id,
				'result': home_team_match.result(match.home_team)
			})
		result['recent_matches_away_team'] = []
		for away_team_match in match.away_team.recent(b, 5):
			result['recent_matches_away_team'].append({
				'id': away_team_match.id,
				'result': away_team_match.result(match.away_team)
			})
	if date.today() <= match.date <= date.today() + timedelta(days=7):
		result['weather'] = weather(match.date, match.time, match.home_team.club.location())

	return jsonify(result)


@bp.route('/teams/<int:id>', methods=['GET'])
def team(id):
	team = Team.query.get(id)
	if not team:
		abort(404)
	result = team.serialize()
	result['recent_matches'] = [match.serialize() for match in team.recent(date.today(), 3)]
	result['future_matches'] = [match.serialize() for match in team.future(date.today())]
	result['club'] = team.club.serialize()
	return jsonify(result)
