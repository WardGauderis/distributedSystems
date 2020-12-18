import jwt
import requests
from flask import render_template, request, url_for, redirect, flash, abort
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.exceptions import HTTPException
from werkzeug.urls import url_parse

from . import bp, login
from .forms import *


@bp.app_errorhandler(HTTPException)
def error_handler(error):
	flash(f'{error.code}: {error.description}', 'danger')
	return redirect(url_for('frontend.index'))


@bp.route('/', methods=['GET'], defaults={'season': 0})
@bp.route('/<int:season>', methods=['GET'])
def index(season):
	divisions = requests.get(f'http://nginx/api/crud/divisions').json()
	stats = requests.get(f'http://nginx/api/stats/top/{season}').json()
	seasons = requests.get('http://nginx/api/crud/seasons').json()
	return render_template('index.html', stats=stats, seasons=seasons, season=season, divisions=divisions)


@bp.route('/divisions/<int:div>/<int:team>/<int:season>', methods=['GET'])
def divisions(div, team, season):
	try:
		divisions = requests.get(f'http://nginx/api/crud/divisions').json()
		division = divisions[div - 1]
		seasons = requests.get(f'http://nginx/api/crud/seasons').json()

		fixtures = requests.get(f'http://nginx/api/stats/fixtures/{div}/{team}/{season}').json()
		table = requests.get(f'http://nginx/api/stats/league_tables/{div}/{season}').json()

		weeks = sorted(set(map(lambda fixture: int(fixture['matchweek']), fixtures)))
		fixtures = {week: [fixture for fixture in fixtures if int(fixture['matchweek']) == week] for week in weeks}

		return render_template('division.html', table=table, fixtures=fixtures, seasons=seasons, division=division,
							   season=season, team=str(team), divisions=divisions)
	except:
		abort(404)


@bp.route('/teams/<int:id>', methods=['GET'])
def teams(id):
	try:
		divisions = requests.get(f'http://nginx/api/crud/divisions').json()
		team = requests.get(f'http://nginx/api/stats/teams/{id}').json()
		try:
			division = divisions[int(team['recent_matches'][0]['division_id']) - 1]['name']
		except:
			division = None
		return render_template('team.html', divisions=divisions, team=team, division=division)
	except:
		abort(404)


@bp.route('/fixtures/<int:id>', methods=['GET'])
def fixtures(id):
	try:
		divisions = requests.get(f'http://nginx/api/crud/divisions').json()
		fixture = requests.get(f'http://nginx/api/stats/fixtures/{id}').json()
		return render_template('fixture.html', divisions=divisions, fixture=fixture)
	except:
		raise
		abort(404)


########################################################################################################################


class User(object):
	def __init__(self, token):
		self.token = token
		self.id = jwt.decode(token, algorithms=['HS256'], verify=False)['id']
		user = requests.get(f'http://nginx/api/crud/users/{self.id}',
							headers={'Authorization': f'Bearer {self.token}'}).json()
		self.is_admin = user['is_admin']
		self.is_super_admin = user['is_super_admin']
		self.stam_number = user.get('stam_number')
		self.team_id = user.get('team_id')

	@property
	def is_active(self):
		return True

	@property
	def is_authenticated(self):
		return True

	@property
	def is_anonymous(self):
		return False

	def get_id(self):
		return self.token


@login.user_loader
def load_user(token):
	try:
		user = User(token)
	except:
		user = None
	return user


@bp.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('frontend.index'))
	form = LoginForm()
	if form.validate_on_submit():
		json = requests.post(f'http://nginx/api/auth', auth=(form.username.data, form.password.data)).json()
		if 'token' in json:
			token = json['token']
			login_user(User(token))
			next_page = request.args.get('next')
			if not next_page or url_parse(next_page).netloc != '':
				next_page = url_for('frontend.index')
			return redirect(next_page)
		flash('Invalid username or password', 'danger')
	divisions = requests.get(f'http://nginx/api/crud/divisions').json()
	return render_template('login.html', form=form, divisions=divisions)


@bp.route('/logout', methods=['GET'])
@login_required
def logout():
	logout_user()
	return redirect(url_for('frontend.index'))


########################################################################################################################


@bp.route('/clubs', methods=['GET'])
@login_required
def clubs_admin():
	if not (current_user.is_admin or current_user.is_super_admin):
		flash('Not authorized to access this page.', 'danger')
		return redirect(url_for('frontend.index'))
	divisions = requests.get(f'http://nginx/api/crud/divisions').json()
	clubs = requests.get(f'http://nginx/api/crud/clubs').json()
	return render_template('clubs.html', divisions=divisions, clubs=clubs)


@bp.route('/teams', methods=['GET'])
@login_required
def teams_admin():
	if not (current_user.is_admin or current_user.is_super_admin):
		flash('Not authorized to access this page.', 'danger')
		return redirect(url_for('frontend.index'))
	divisions = requests.get(f'http://nginx/api/crud/divisions').json()
	teams = requests.get(f'http://nginx/api/crud/teams').json()
	return render_template('teams.html', divisions=divisions, teams=teams)


@bp.route('/divisions', methods=['GET'])
@login_required
def divisions_admin():
	if not (current_user.is_admin or current_user.is_super_admin):
		flash('Not authorized to access this page.', 'danger')
		return redirect(url_for('frontend.index'))
	divisions = requests.get(f'http://nginx/api/crud/divisions').json()
	return render_template('divisions.html', divisions=divisions)


@bp.route('/matches', methods=['GET'])
@login_required
def matches_admin():
	if not (current_user.is_admin or current_user.is_super_admin):
		flash('Not authorized to access this page.', 'danger')
		return redirect(url_for('frontend.index'))
	divisions = requests.get(f'http://nginx/api/crud/divisions').json()
	queries = {'division_id': int(request.args.get('division_id', default=0)),
			   'season': int(request.args.get('season', default=0))}
	matches = requests.get(f'http://nginx/api/crud/matches', queries).json()
	seasons = requests.get(f'http://nginx/api/crud/seasons').json()
	return render_template('matches.html', divisions=divisions, matches=matches, season=int(queries['season']),
						   division=queries['division_id'], seasons=seasons)


@bp.route('/referees', methods=['GET'])
@login_required
def referees_admin():
	if not (current_user.is_admin or current_user.is_super_admin):
		flash('Not authorized to access this page.', 'danger')
		return redirect(url_for('frontend.index'))
	divisions = requests.get(f'http://nginx/api/crud/divisions').json()
	referees = requests.get(f'http://nginx/api/crud/referees',
							headers={'Authorization': f'Bearer {current_user.token}'}).json()
	return render_template('referees.html', divisions=divisions, referees=referees)


@bp.route('/users', methods=['GET'])
@login_required
def users_admin():
	if not (current_user.is_admin or current_user.is_super_admin):
		flash('Not authorized to access this page.', 'danger')
		return redirect(url_for('frontend.index'))
	divisions = requests.get(f'http://nginx/api/crud/divisions').json()
	users = requests.get(f'http://nginx/api/crud/users',
						 headers={'Authorization': f'Bearer {current_user.token}'}).json()
	return render_template('users.html', divisions=divisions, users=users)


########################################################################################################################


def update(type, title, form, id, not_admin=False):
	if not not_admin and not (current_user.is_admin or current_user.is_super_admin):
		flash('Not authorized to access this page.', 'danger')
		return redirect(url_for('frontend.index'))

	divisions = requests.get(f'http://nginx/api/crud/divisions').json()

	if 'delete' in request.form and not not_admin:
		r = requests.delete(f'http://nginx/api/crud/{type}/{id}', json=form.to_json(),
							headers={'Authorization': f'Bearer {current_user.token}'})
		r.raise_for_status()
		return redirect(url_for(f'frontend.{type}_admin'))

	if form.validate_on_submit():
		if type == 'matches' and not_admin:
			r = requests.patch(f'http://nginx/api/crud/{type}/{id}', json=form.to_json(),
							   headers={'Authorization': f'Bearer {current_user.token}'})
		else:
			r = requests.put(f'http://nginx/api/crud/{type}/{id}', json=form.to_json(),
							 headers={'Authorization': f'Bearer {current_user.token}'})
		r.raise_for_status()
		if r.ok:
			if type == 'users' and current_user.is_super_admin:
				if form.is_admin.data:
					requests.post(f'http://nginx/api/crud/admins/{id}',
								  headers={'Authorization': f'Bearer {current_user.token}'})
				else:
					requests.delete(f'http://nginx/api/crud/admins/{id}',
									headers={'Authorization': f'Bearer {current_user.token}'})
			if not_admin:
				if type == 'matches':
					return redirect(url_for(f'frontend.scores'))
				return redirect(url_for(f'frontend.index'))
			return redirect(url_for(f'frontend.{type}_admin'))
		flash(r.json()['description'], 'danger')
		return render_template('form.html', title=title, form=form, divisions=divisions)
	json = requests.get(f'http://nginx/api/crud/{type}/{id}',
						headers={'Authorization': f'Bearer {current_user.token}'}).json()
	form.from_json(json)
	return render_template('form.html', title=title, form=form, divisions=divisions)


def create(type, title, form):
	if not (current_user.is_admin or current_user.is_super_admin):
		flash('Not authorized to access this page.', 'danger')
		return redirect(url_for('frontend.index'))

	form.update.label.text = 'Create'
	form.delete.widget = HiddenInput()

	divisions = requests.get(f'http://nginx/api/crud/divisions').json()

	if form.validate_on_submit():
		r = requests.post(f'http://nginx/api/crud/{type}', json=form.to_json(),
						  headers={'Authorization': f'Bearer {current_user.token}'})
		if r.ok:
			if type == 'users' and current_user.is_super_admin:
				if form.is_admin.data:
					requests.post(f'http://nginx/api/crud/admins/{r.json()["id"]}',
								  headers={'Authorization': f'Bearer {current_user.token}'})

			return redirect(url_for(f'frontend.{type}_admin'))
		flash(r.json()['description'], 'danger')
		return render_template('form.html', title=title, form=form, divisions=divisions)

	return render_template('form.html', title=title, form=form, divisions=divisions)


@bp.route('/clubs/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def club_admin(id):
	try:
		form = ClubForm()
		club_and_not_admin = current_user.stam_number == id and not (
				current_user.is_admin or current_user.is_super_admin)
		if club_and_not_admin:
			form.delete.widget = HiddenInput()
		return update('clubs', 'Club', form, id, club_and_not_admin)
	except:
		abort(404)


@bp.route('/clubs/add', methods=['GET', 'POST'])
@login_required
def club_create_admin():
	return create('clubs', 'Club', ClubForm())


@bp.route('/teams/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def team_admin(id):
	try:
		form = TeamForm()
		clubs = requests.get(f'http://nginx/api/crud/clubs').json()
		form.stam_number.choices = [(club['stam_number'], club['name']) for club in clubs]
		return update('teams', 'Team', form, id)
	except:
		abort(404)


@bp.route('/teams/add', methods=['GET', 'POST'])
@login_required
def team_create_admin():
	form = TeamForm()
	clubs = requests.get(f'http://nginx/api/crud/clubs').json()
	form.stam_number.choices = [(club['stam_number'], club['name']) for club in clubs]
	return create('teams', 'Team', form)


@bp.route('/divisions/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def division_admin(id):
	try:
		return update('divisions', 'Division', DivisionForm(), id)
	except:
		abort(404)


@bp.route('/divisions/add', methods=['GET', 'POST'])
@login_required
def division_create_admin():
	return create('divisions', 'Division', DivisionForm())


@bp.route('/matches/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def match_admin(id):
	try:
		match = requests.get(f'http://nginx/api/crud/matches/{id}').json()
		team_and_not_admin = current_user.team_id == match['home_team_id'] and not (
				current_user.is_admin or current_user.is_super_admin)

		if team_and_not_admin:
			form = ScoreForm()
		else:
			form = MatchForm()
			teams = requests.get(f'http://nginx/api/crud/teams').json()
			referees = requests.get(f'http://nginx/api/crud/referees',
									headers={'Authorization': f'Bearer {current_user.token}'}).json()
			divisions = requests.get(f'http://nginx/api/crud/divisions').json()
			form.home_team_id.choices = [(team['id'], team['name']) for team in teams]
			form.away_team_id.choices = [(team['id'], team['name']) for team in teams]
			form.referee_id.choices = [('', '---')] + [
				(referee['id'], referee['first_name'] + ' ' + referee['last_name'] + ' (' + referee['date_of_birth'] + ')')
				for
				referee in referees]
			form.division_id.choices = [(division['id'], division['name']) for division in divisions]
		return update('matches', 'Match', form, id, team_and_not_admin)
	except:
		abort(404)


@bp.route('/matches/add', methods=['GET', 'POST'])
@login_required
def match_create_admin():
	form = MatchForm()
	teams = requests.get(f'http://nginx/api/crud/teams').json()
	referees = requests.get(f'http://nginx/api/crud/referees',
							headers={'Authorization': f'Bearer {current_user.token}'}).json()
	divisions = requests.get(f'http://nginx/api/crud/divisions').json()
	form.home_team_id.choices = [(team['id'], team['name']) for team in teams]
	form.away_team_id.choices = [(team['id'], team['name']) for team in teams]
	form.referee_id.choices = [('', '---')] + [
		(referee['id'], referee['first_name'] + ' ' + referee['last_name'] + ' (' + referee['date_of_birth'] + ')') for
		referee in referees]
	form.division_id.choices = [(division['id'], division['name']) for division in divisions]
	return create('matches', 'Match', form)


@bp.route('/referees/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def referee_admin(id):
	try:
		return update('referees', 'Referee', RefereeForm(), id)
	except:
		abort(404)


@bp.route('/referees/add', methods=['GET', 'POST'])
@login_required
def referee_create_admin():
	return create('referees', 'Referee', RefereeForm())


@bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def user_admin(id):
	try:
		form = UserForm()
		teams = requests.get(f'http://nginx/api/crud/teams').json()
		form.team_id.choices = [('', '---')] + [(team['id'], team['name']) for team in teams]
		if not current_user.is_super_admin:
			form.is_admin.render_kw = {'disabled': True}
		return update('users', 'User', form, id)
	except:
		abort(404)


@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
def user_create_admin():
	form = UserForm()
	form.password.validators = [DataRequired()]
	teams = requests.get(f'http://nginx/api/crud/teams').json()
	form.team_id.choices = [('', '---')] + [(team['id'], team['name']) for team in teams]
	if not current_user.is_super_admin:
		form.is_admin.render_kw = {'disabled': True}
	return create('users', 'User', form)


########################################################################################################################

@bp.route('/scores', methods=['GET'])
@login_required
def scores():
	if current_user.team_id is None:
		flash('Not authorized to access this page.', 'danger')
		return redirect(url_for('frontend.index'))
	divisions = requests.get(f'http://nginx/api/crud/divisions').json()
	queries = {'division_id': int(request.args.get('division_id', default=0)),
			   'season': int(request.args.get('season', default=0)),
			   'team_id': current_user.team_id}
	matches = requests.get(f'http://nginx/api/crud/matches', queries).json()
	seasons = requests.get(f'http://nginx/api/crud/seasons').json()
	return render_template('matches.html', divisions=divisions, matches=matches, season=int(queries['season']),
						   division=queries['division_id'], seasons=seasons)
