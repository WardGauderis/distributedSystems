from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
from wtforms.fields.html5 import *
from wtforms.widgets import HiddenInput
from datetime import date, time


class GeneralForm(FlaskForm):
	def from_json(self, json):
		for key, value in json.items():
			if hasattr(self, key):
				attr = getattr(self, key)
				attr.process_formdata([value])

	def to_json(self):
		json = {}
		for attr, value in self.__dict__.items():
			if hasattr(value, 'data') and not (attr == 'update' or attr == 'delete'):
				if type(value.data) == time or type(value.data) == date:
					json[attr] = str(value.data)
				else:
					json[attr] = value.data
		return json


class LoginForm(GeneralForm):
	username = StringField('Username', [DataRequired(), Length(max=64)])
	password = PasswordField('Password', [DataRequired()])
	submit = SubmitField('Log In')


class ClubForm(GeneralForm):
	name = StringField('Name', [DataRequired(), Length(max=64)])
	address = StringField('Address', [DataRequired(), Length(max=128)])
	zip_code = IntegerField('Zip Code', [DataRequired()])
	city = StringField('City', [DataRequired(), Length(max=64)])
	website = StringField('Website', [Length(max=128)])
	update = SubmitField('Update')
	delete = SubmitField('Delete')


class TeamForm(GeneralForm):
	stam_number = SelectField('Club', [DataRequired()])
	suffix = StringField('Suffix', [Length(max=32)])
	colors = StringField('Colors', [DataRequired(), Length(max=128)])
	update = SubmitField('Update')
	delete = SubmitField('Delete')


class DivisionForm(GeneralForm):
	name = StringField('Name', [DataRequired(), Length(max=64)])
	update = SubmitField('Update')
	delete = SubmitField('Delete')


class MatchForm(GeneralForm):
	division_id = SelectField('Division', [DataRequired()])
	matchweek = IntegerField('Week', [DataRequired(), NumberRange(min=1)])
	date = DateField('Date', [DataRequired()])
	time = TimeField('Kickoff Time', [DataRequired()], format='%H:%M:%S', render_kw={'step': '1'})
	home_team_id = SelectField('Home Team', [DataRequired()])
	away_team_id = SelectField('Away Team', [DataRequired()])
	goals_home_team = IntegerField('Goals Home Team', [Optional(), NumberRange(min=0)])
	goals_away_team = IntegerField('Goals Away Team', [Optional(), NumberRange(min=0)])
	status = SelectField('Status',
						 choices=[('', '---'), ('Postponed', 'Postponed'), ('Canceled', 'Canceled'),
								  ('Forfait', 'Forfait')])
	referee_id = SelectField('Referee')
	update = SubmitField('Update')
	delete = SubmitField('Delete')


class ScoreForm(GeneralForm):
	goals_home_team = IntegerField('Goals Home Team', [Optional(), NumberRange(min=0)])
	goals_away_team = IntegerField('Goals Away Team', [Optional(), NumberRange(min=0)])
	update = SubmitField('Update')


class RefereeForm(GeneralForm):
	first_name = StringField('First Name', [DataRequired(), Length(max=64)])
	last_name = StringField('Last Name', [DataRequired(), Length(max=64)])
	address = StringField('Address', [DataRequired(), Length(max=128)])
	zip_code = IntegerField('Zip Code', [DataRequired()])
	city = StringField('City', [DataRequired(), Length(max=64)])
	phone_number = TelField('Phone Number', [DataRequired(), Length(max=64)])
	email = EmailField('Email', [DataRequired(), Length(max=128)])
	date_of_birth = DateField('Date of Birth', [DataRequired()])
	update = SubmitField('Update')
	delete = SubmitField('Delete')


class UserForm(GeneralForm):
	username = StringField('Username', [DataRequired(), Length(max=64)])
	password = PasswordField('Password')
	email = EmailField('Email', [DataRequired(), Length(max=128)])
	team_id = SelectField('Team')
	is_admin = BooleanField('Admin')
	is_super_admin = BooleanField('Super Admin', render_kw={'disabled': True})
	update = SubmitField('Update')
	delete = SubmitField('Delete')

	def to_json(self):
		json = super().to_json()
		if json.get('password') == '':
			json.pop('password')
		return json
