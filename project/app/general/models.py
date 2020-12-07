import jwt
from datetime import datetime, timedelta
from app.service import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app


class Club(db.Model):
	stam_number = db.Column(db.Integer(), db.Sequence('club_stam_number_seq', start=333, increment=1), primary_key=True)
	name = db.Column(db.String(64), nullable=False, unique=True)
	address = db.Column(db.String(128), nullable=False)
	zip_code = db.Column(db.Integer(), nullable=False)
	city = db.Column(db.String(64), nullable=False)
	website = db.Column(db.String(128))


class Team(db.Model):
	__table_args__ = (db.UniqueConstraint('suffix', 'stam_number'),)
	id = db.Column(db.Integer(), db.Sequence('team_id_seq', start=71, increment=1), primary_key=True)
	stam_number = db.Column(db.Integer(), db.ForeignKey('club.stam_number'), nullable=False)
	suffix = db.Column(db.String(32))
	colors = db.Column(db.String(128), nullable=False)


class Division(db.Model):
	id = db.Column(db.Integer(), db.Sequence('division_id_seq', start=7, increment=1), primary_key=True)
	name = db.Column(db.String(64), nullable=False, unique=True)


class Match(db.Model):
	__table_args__ = (db.UniqueConstraint('date', 'time', 'home_team_id', 'away_team_id'),
					  db.CheckConstraint('home_team_id != away_team_id'),
					  db.CheckConstraint('matchweek > 0'),
					  db.CheckConstraint('goals_home_team >= 0 and goals_away_team >= 0'),
					  db.UniqueConstraint('referee_id', 'date'),
					  db.UniqueConstraint('home_team_id', 'date'),
					  db.UniqueConstraint('away_team_id', 'date'))
	id = db.Column(db.Integer(), primary_key=True)
	division_id = db.Column(db.Integer(), db.ForeignKey('division.id', ondelete='cascade'), nullable=False)
	matchweek = db.Column(db.Integer(), nullable=False)
	date = db.Column(db.Date(), nullable=False)  # TODO match matchweek
	time = db.Column(db.Time(), nullable=False)
	home_team_id = db.Column(db.Integer(), db.ForeignKey('team.id', ondelete='cascade'), nullable=False)
	away_team_id = db.Column(db.Integer(), db.ForeignKey('team.id', ondelete='cascade'), nullable=False)
	goals_home_team = db.Column(db.Integer())  # TODO null??
	goals_away_team = db.Column(db.Integer())
	status = db.Column(db.Enum('Postponed', 'Canceled', 'Forfait', name='match_status'))
	referee_id = db.Column(db.Integer(), db.ForeignKey('referee.id'))


class Referee(db.Model):
	__table_args__ = (db.UniqueConstraint('first_name', 'last_name', 'date_of_birth'),)
	id = db.Column(db.Integer(), primary_key=True)
	first_name = db.Column(db.String(64), nullable=False)
	last_name = db.Column(db.String(64), nullable=False)
	address = db.Column(db.String(128), nullable=False)
	zip_code = db.Column(db.Integer(), nullable=False)
	city = db.Column(db.String(64), nullable=False)
	phone_number = db.Column(db.String(64), nullable=False)  # TODO check (niet in db)
	email = db.Column(db.String(128), nullable=False)
	date_of_birth = db.Column(db.Date(), nullable=False)


class User(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	username = db.Column(db.String(64), nullable=False, unique=True)
	password_hash = db.Column(db.String(128), nullable=False)
	email = db.Column(db.String(128), nullable=False)
	team_id = db.Column(db.Integer(), db.ForeignKey('team.id'))
	is_admin = db.Column(db.Boolean(), nullable=False)
	is_super_admin = db.Column(db.Boolean(), nullable=False)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def get_token(self):
		return jwt.encode(
			{'id': self.id, 'exp': datetime.utcnow() + timedelta(minutes=30)},
			current_app.config['SECRET_KEY'],
			algorithm='HS256',
		).decode('utf-8')
