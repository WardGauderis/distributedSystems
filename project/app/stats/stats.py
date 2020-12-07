from datetime import date

from flask import jsonify, abort

from app.general.models import Division, Match, Team
from . import bp


def get_season_start_and_end(season, past=True):
	# 1: 2018/1 2019/22 09-04 -> 04-24
	# year - 2017 - week >= 15
	# 6 : year - 2017 - week >= 17
	if season <= 0:
		if past: return date(1, 9, 4), date.today()
		else: return date.today(), date(3000, 1, 1)
	return date(season, 9, 4), min(date(season + 1, 4, 25), date.today())


@bp.route('/league_table/<int:div>/<int:season>', methods=['GET'])
def league_table(div, season):
	division = Division.query.get(div) or abort(404)
	try:
		a, b = get_season_start_and_end(season)
		teams = division.teams(a, b).all()
		return jsonify([{
			'id': team.id,
			'name': team.name(),
			'played': team.played(division, a, b),
			'won': team.won(division, a, b),
			'drawn': team.drawn(division, a, b),
			'lost': team.lost(division, a, b),
			'GF': team.gf(division, a, b),
			'GA': team.ga(division, a, b),
			'GD': team.gd(division, a, b)
		} for team in teams])
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
