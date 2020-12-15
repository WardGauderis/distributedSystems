from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *


class GeneralForm(FlaskForm):
	def from_json(self, json):
		for key, value in json.items():
			if hasattr(self, key):
				attr = getattr(self, key)
				print(attr)
				import sys
				sys.stdout.flush()
				attr.process_formdata([value])

	def to_json(self):
		json = {}
		for attr, value in self.__dict__.items():
			if hasattr(value, 'data') and not (attr == 'update' or attr == 'delete'):
				json[attr] = value.data
		return json


class LoginForm(GeneralForm):
	username = StringField('Username', [DataRequired()])
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
	time = TimeField('Kickoff Time', [DataRequired()])
	home_team_id = SelectField('Home Team', [DataRequired()])
	away_team_id = SelectField('Away Team', [DataRequired()])
	goals_home_team = IntegerField('Goals Home Team', [NumberRange(min=0)])
	goals_away_team = IntegerField('Goals Away Team', [NumberRange(min=0)])
	status = SelectField('Status',
						 choices=[('Postponed', 'Postponed'), ('Canceled', 'Canceled'), ('Forfait', 'Forfait')])
	referee_id = SelectField('Referee')
	update = SubmitField('Update')
	delete = SubmitField('Delete')
