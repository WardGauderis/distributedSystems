from database import db


class Club(db.Model):  # TODO sequence with premade data
	stam_number = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(64), nullable=False)  # TODO empty? ...
	address = db.Column(db.String(128), nullable=False)
	zip_code = db.Column(db.Integer(), nullable=False)
	city = db.Column(db.String(64), nullable=False)
	website = db.Column(db.String(128))


class Team(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	stam_number = db.Column(db.Integer(), db.ForeignKey('club.stam_number'), nullable=False)
	suffix = db.Column(db.String(32))  # unique per stam nummer
	colors = db.Column(db.String(128), nullable=False)


class Division(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(64), nullable=False)


class Match(db.Model):  # TODO unique, referee (double booked), niet tegen zichzelf spelen
	id = db.Column(db.Integer(), primary_key=True)
	division_id = db.Column(db.Integer(), db.ForeignKey('division.id'), nullable=False)  # TODO on delete/update? ...
	matchweek = db.Column(db.Integer(), nullable=False)  # TODO > 0
	date = db.Column(db.Date(), nullable=False)  # TODO match mathcweek
	time = db.Column(db.Time(), nullable=False)
	home_team_id = db.Column(db.Integer(), db.ForeignKey('team.id'), nullable=False)
	away_team_id = db.Column(db.Integer(), db.ForeignKey('team.id'), nullable=False)
	goals_home_team = db.Column(db.Integer())  # TODO > 0, null als nog niet gespeeld ...
	goals_away_team = db.Column(db.Integer())
	status = db.Column(db.Enum('Postponed', 'Canceled', 'Forfait', name='match_status'))


class Referee(db.Model):  # TODO unique
	id = db.Column(db.Integer(), primary_key=True)
	first_name = db.Column(db.String(64), nullable=False)
	last_name = db.Column(db.String(64), nullable=False)
	address = db.Column(db.String(128), nullable=False)
	zip_code = db.Column(db.Integer(), nullable=False)
	city = db.Column(db.String(64), nullable=False)
	phone_number = db.Column(db.String(64), nullable=False)  # TODO checks
	email = db.Column(db.String(128), nullable=False)
	date_of_birth = db.Column(db.Date(), nullable=False)


class User(db.Model):  # TODO unique
	id = db.Column(db.Integer(), primary_key=True)
	username = db.Column(db.String(64), nullable=False)
	password_hash = db.Column(db.String(128), nullable=False)
	email = db.Column(db.String(128), nullable=False)
	team_id = db.Column(db.Integer(), db.ForeignKey('team.id'))
	is_admin = db.Column(db.Boolean(), nullable=False)
	is_super_admin = db.Column(db.Boolean(), nullable=False)
