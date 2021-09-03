import logging

import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Float, String, MetaData
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)

Base = declarative_base()


class Results(Base):
	"""Create a data model for the database to capture player statistics"""
	__tablename__ = 'results'
	player_id = Column(String(100), primary_key=True)
	player_name = Column(String(100), unique=False, nullable=False)
	year = Column(String(100), unique=False, nullable=False)
	position = Column(String(100), unique=False, nullable=False)
	height = Column(Integer, unique=False, nullable=False)
	weight = Column(Integer, unique=False, nullable=False)
	player_type = Column(String(100), unique=False, nullable=False)
	team = Column(String(100), unique=False, nullable=False)
	conference = Column(String(100), unique=False, nullable=False)
	games = Column(Integer, unique=False, nullable=False)
	games_started = Column(Integer, unique=False, nullable=False)
	fg_pct = Column(Float, unique=False, nullable=False)
	fg_pct3 = Column(Float, unique=False, nullable=False)
	ft_pct = Column(Float, unique=False, nullable=False)
	points = Column(Integer, unique=False, nullable=False)
	ppm = Column(Float, unique=False, nullable=False)
	assists = Column(Integer, unique=False, nullable=False)
	apm = Column(Float, unique=False, nullable=False)
	a_perc = Column(Float, unique=False, nullable=False)
	rebounds = Column(Integer, unique=False, nullable=False)
	rpm = Column(Float, unique=False, nullable=False)
	r_perc = Column(Float, unique=False, nullable=False)
	blocks = Column(Integer, unique=False, nullable=False)
	bpm = Column(Float, unique=False, nullable=False)
	b_perc = Column(Float, unique=False, nullable=False)
	steals = Column(Integer, unique=False, nullable=False)
	spm = Column(Float, unique=False, nullable=False)
	s_perc = Column(Float, unique=False, nullable=False)
	turnovers = Column(Integer, unique=False, nullable=False)
	tpm = Column(Float, unique=False, nullable=False)
	t_perc = Column(Float, unique=False, nullable=False)
	usage = Column(Float, unique=False, nullable=False)
	efficiency = Column(Float, unique=False, nullable=False)

	def __repr__(self):
		return '<Results %r>' % self.title


def create_db(engine_string: str):
	"""
    Create a database using SQLAlchemy on AWS RDS or locally with SQLite
    Args:
        engine_string: (String), Required: RDS connection engine string
    Returns:
        None
    """
	try:
		# Set up mysql or sqlite connection
		engine = sql.create_engine(engine_string)

		# Create the Results table
		Base.metadata.create_all(engine)

		# Catch exceptions when connecting to database
	except sql.exc.DBAPIError:
		logger.error('General database connection error. Please check if you are connected to the internet or any necessary VPNs and try again.')
	except sql.exc.SQLAlchemyError:
		logger.error('An unexpected error occurred. Please check your engine string format and if you are connected to the internet and/or VPNs and try again.')
	else:
		logger.warning('If you used environment variables and if they were not exported correctly, the default database location of sqlite:///data/results.db may have been used.')
		logger.info('Database and results table created with provided or default engine string.')

class ResultsManager:

	def __init__(self, app=None, engine_string=None):
		"""
		Initialize ResultsManager class in order to modify the Results table
		Args:
    		app: Flask - Flask app
			engine_string: str - Engine string
		Returns: None
		"""
		# If an app is input, create a database session from the app
		if app:
			try:
				self.db = SQLAlchemy(app)
				self.session = self.db.session
			# Catch all exceptions when connecting to the database
			except sql.exc.DBAPIError:
				logger.error('General database connection error. Please check if you are connected to the internet and/or VPNs and try again.')
			except sql.exc.SQLAlchemyError:
				logger.error('An unexpected error occurred. Please check you are connected to the internet and/or VPNs and try again.')
		# If an engine_string is the input, create a database session from the engine string
		elif engine_string:
			try:
				engine = sql.create_engine(engine_string)
				Session = sessionmaker(bind=engine)
				self.session = Session()
			# Catch all exceptions when connecting to the database
			except sql.exc.DBAPIError:
				logger.error('General database connection error. Please check if you are connected to the internet or any necessary VPNs and try again.')
			except sql.exc.SQLAlchemyError:
				logger.error('An unexpected error occurred. Please check your engine string format and if you are connected to the internet and/or VPNs and try again.')
			else:
				logger.warning('If you used environment variables and if they were not exported correctly, the default database location of sqlite:///data/results.db may have been used.')
		else:
			raise ValueError('Need either an engine string or a Flask app to initialize')


	def close(self) -> None:
		"""Closes session
		Returns: None
		"""
		self.session.close()


	def add_player(self,player_id,name,year,position,height,weight,
        player_type,team,conference,games_played,games_started,
        field_goal_percentage,three_point_percentage,free_throw_percentage,points,
        ppm,assists,apm,assist_percentage,total_rebounds,rpm,
        total_rebound_percentage,blocks,bpm,block_percentage,steals,
        spm,steal_percentage,turnovers,tpm,turnover_percentage,
        usage_percentage,player_efficiency_rating):
		"""Populates an existing database with player data
        Args:
            player_id (String): Unique player identifier
			name (String): Full player name
			year (String): Player college class
			position (String): Standard player position
			height (int): Player height in inches
			weight (int): Player weight in pounds
		    player_type (String): New player types generated from clustering
			team (String): Player team for prior season
			conference (String): Player conference from prior season
			games_played (int): Player games played in prior season
			games_started (int): Player games started in prior season
		    field_goal_percentage (float): Player shot percentage prior season
			three_point_percentage (float): Player 3-point shot percentage prior season
			free_throw_percentage (float): Player free throw percentage prior season
			points (int): Player total points
		    ppm (float): Player points per minute
			assists (int): Player total assists
			apm (float): PLayer assists per minute
			assist_percentage (float): Player assist percentage
			total_rebounds (int): Player total rebounds
			rpm (float): Player rebounds per minute
		    total_rebound_percentage (float): Player rebound percentage
			blocks (int): Player total blocks
			bpm (float): Player blocks per minute
			block_percentage (float): Player block percentage
			steals (int): Player total steals
		    spm (float): Player steals per minute
			steal_percentage (float): Player steal percentage
			turnovers (int): Player total turnovers
			tpm (float): Player turnovers per minute
			turnover_percentage (float): Player turnover percentage
		    usage_percentage (float): Player usage percentage
			player_efficiency_rating (float): Player efficiency metric
        Returns: None
        """
		# Create database session
		session = self.session

		# Add one row for stats of one player to database
		player = Results(player_id=player_id,player_name=name,year=year,position=position,height=height,weight=weight,
	        player_type=player_type,team=team,conference=conference,games=games_played,games_started=games_started,
	        fg_pct=field_goal_percentage,fg_pct3=three_point_percentage,ft_pct=free_throw_percentage,points=points,
	        ppm=ppm,assists=assists,apm=apm,a_perc=assist_percentage,rebounds=total_rebounds,rpm=rpm,
	        r_perc=total_rebound_percentage,blocks=blocks,bpm=bpm,b_perc=block_percentage,steals=steals,
	        spm=spm,s_perc=steal_percentage,turnovers=turnovers,tpm=tpm,t_perc=turnover_percentage,
	        usage=usage_percentage,efficiency=player_efficiency_rating)
		session.add(player)

		# Commit changes to database
		session.commit()
