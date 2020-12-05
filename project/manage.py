from flask.cli import FlaskGroup
from database import create_app, db
import database.models
import pandas

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command()
def recreate_db():
	db.drop_all()
	db.create_all()
	clubs = pandas.read_csv('database/data/clubs.csv')
	clubs.to_sql('club', db.engine, if_exists='append', index=False)
	divisions = pandas.read_csv('database/data/divisions.csv')
	divisions.to_sql('division', db.engine, if_exists='append', index=False)
	referees = pandas.read_csv('database/data/referees.csv')
	referees.to_sql('referee', db.engine, if_exists='append', index=False)
	teams = pandas.read_csv('database/data/teams.csv')
	teams.to_sql('team', db.engine, if_exists='append', index=False)
	matches = pandas.read_csv('database/data/matches_2018_2019.csv')
	matches.to_sql('match', db.engine, if_exists='append', index=False)
	matches = pandas.read_csv('database/data/matches_2019_2020.csv')
	matches.to_sql('match', db.engine, if_exists='append', index=False)
	matches = pandas.read_csv('database/data/matches_2020_2021.csv')
	matches.to_sql('match', db.engine, if_exists='append', index=False)
	db.session.commit()



if __name__ == '__main__':
	cli()
