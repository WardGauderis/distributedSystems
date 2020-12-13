import jwt
import requests
from flask import render_template, request, url_for, redirect, flash
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.urls import url_parse
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *

from . import bp, login


# TODO check foutief

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


class User(object):
	def __init__(self, token):
		self.token = token
		self.id = jwt.decode(token, algorithms=['HS256'], verify=False)['id']
		user = requests.get(f'http://nginx/api/crud/users/{self.id}',
							headers={'Authorization': f'Bearer {self.token}'}).json()
		self.is_admin = user['is_admin'] == 'True'
		self.is_super_admin = user['is_super_admin'] == 'True'
		self.has_team = 'team_id' in user

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
	return User(token)


class LoginForm(FlaskForm):
	username = StringField('Username', [DataRequired()])
	password = PasswordField('Password', [DataRequired()])
	submit = SubmitField('Log In')


@bp.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
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
	return render_template('login.html', form=form)


@bp.route('/logout', methods=['GET'])
@login_required
def logout():
	logout_user()
	return redirect(url_for('frontend.index'))
