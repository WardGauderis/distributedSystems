from . import bp
from flask import jsonify, abort
from app.general.models import Division
from datetime import date


# 1: 2018/1 2019/22 09-04 -> 04-24
# year - 2017 - week >= 15
# 6 : year - 2017 - week >= 17

def get_season_start_and_end(season):
	return date(2017 + season, 9, 4), date(2017 + season + 1, 4, 24)


@bp.route('/league_table/<int:id>/<int:season>', methods=['GET'])
def league_table(id, season):
	try:
		if season < 1:
			abort(400)
		division = Division.query.get(id)
		a, b = get_season_start_and_end(season)
		b = min(b, date.today())
		print(b)
		teams = division.teams(a).all()
		import sys
		sys.stdout.flush()
		return jsonify([{
			'id': team.id,
			'played': team.played(division, a, b),
			'won': team.won(division, a, b),
			'drawn': team.drawn(division, a, b),
			'lost': team.lost(division, a, b),
			'GF': team.gf(division, a, b),
			'GA': team.ga(division, a, b),
			'GD': team.gd(division, a, b)
		} for team in teams])
	except:
		raise
		abort(400)
