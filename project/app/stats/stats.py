import requests
from datetime import date, datetime, timedelta

from flask import jsonify, abort

from app.general.models import Division, Match, Team
from . import bp


def get_season_start_and_end(season, past=True):
	# 1: 2018/1 2019/22 09-04 -> 04-24
	# year - 2017 - week >= 15
	# 6 : year - 2017 - week >= 17
	if season <= 0:
		if past:
			return date(1, 9, 4), date.today()
		else:
			return date.today(), date(3000, 1, 1)
	return date(season, 9, 1), min(date(season + 1, 4, 30), date.today())


def get_season(datum: date):
	return datum.year - (datum < date(datum.year, 4, 30))


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
			'id': weather['weather'][0]['id'],
			'rain': weather['rain'],
			'feels_like': weather['feels_like']['day']
		}
	except:
		return 'Weather/Geolocation service error'


@bp.route('/league_table/<int:div>/<int:season>', methods=['GET'])
def league_table(div, season):
	division = Division.query.get(div) or abort(404)
	try:
		a, b = get_season_start_and_end(season)
		teams = division.teams(a, b)
		result = [{
			'id': team.id,
			'name': team.name(),
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
		print(result)
		return jsonify(result)
	except:
		abort(400)


@bp.route('/fixtures/<int:div>/<int:team>/<int:season>/<int:week>', methods=['GET'])
def fixtures(div, team, season, week):
	try:
		a, b = get_season_start_and_end(season, False)
		query = Match.query.filter(Match.division_id == div).filter(Match.date >= a, Match.date < b)
		if team:
			query = query.filter(Match.home_team_id == team or Match.away_team_id == team)
		if week:
			query = query.filter(Match.matchweek == week)
		matches = query.order_by(Match.date).all()
		result = []
		for match in matches:
			result.append({
				'id': match.id,
				'home_team_id': match.home_team_id,
				'away_team_id': match.away_team_id,
				'home_team_name': match.home_team.name(),
				'away_team_name': match.away_team.name(),
				'date': str(match.date),
				'time': str(match.time)
			})
			if match.status is not None:
				result[len(result) - 1]['status'] = match.status
		return jsonify(result)
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
				'division_id': division.id,
				'division_name': division.name,
				'best_attack': {
					'team_id': attack.id,
					'team_name': attack.name(),
					'GF': gf},
				'best_defence': {
					'team_id': defense.id,
					'team_name': defense.name(),
					'GA': ga},
				'most_clean_sheets': {
					'team_id': sheets.id,
					'team_name': sheets.name(),
					'count': count}
			})
		return jsonify(result)
	except:
		abort(400)


@bp.route('/fixture/<int:id>', methods=['GET'])
def fixture(id):
	match = Match.query.get(id)
	if not match:
		abort(404)
	result = {
		'home_team_id': match.home_team_id,
		'away_team_id': match.away_team_id,
		'home_team_name': match.home_team.name(),
		'away_team_name': match.away_team.name(),
		'date': str(match.date),
		'time': str(match.time)
	}
	if match.referee:
		result['referee_first_name'] = match.referee.first_name
		result['referee_last_name'] = match.referee.last_name
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
			result['recent_matches'].append({
				'id': recent_match.id,
				'home_team_id': recent_match.home_team_id,
				'away_team_id': recent_match.away_team_id,
				'goals_home_team': recent_match.goals_home_team,
				'goalse_away_team': recent_match.goals_away_team
			})

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
	elif match.goals_home_team is not None:
		result['goals_home_team'] = match.goals_home_team
		result['goals_away_team'] = match.goals_away_team
	if date.today() <= match.date <= date.today() + timedelta(days=7):
		result['weather'] = weather(match.date, match.time, match.home_team.club.location())

	return jsonify(result)


@bp.route('/team/<int:id>', methods=['GET'])
def team(id):
	team = Team.query.get(id)
	if not team:
		abort(404)
	result = {
		'id': team.id,
		'colors': team.colors,
		'club_name': team.club.name,
		'stam_number': team.club.stam_number,
		'recent_matches': [{
			'id': match.id,
			'home_team_id': match.home_team_id,
			'away_team_id': match.away_team_id,
			'goals_home_team': match.goals_home_team,
			'goalse_away_team': match.goals_away_team,
			'date': str(match.date)
		} for match in team.recent(date.today(), 3)],
		'future_matches': [{
			'id': match.id,
			'home_team_id': match.home_team_id,
			'away_team_id': match.away_team_id,
			'date': str(match.date)
		} for match in team.future(date.today())]
	}
	if team.suffix:
		result['suffix'] = team.suffix
	return jsonify(result)
