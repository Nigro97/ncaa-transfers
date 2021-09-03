import logging
import requests

import pandas as pd
import botocore
from sportsipy.ncaab.teams import Teams

logger = logging.getLogger(__name__)

logging.getLogger('botocore').setLevel(logging.ERROR)
logging.getLogger('s3transfer').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('asyncio').setLevel(logging.ERROR)
logging.getLogger('aiobotocore').setLevel(logging.ERROR)
logging.getLogger('s3fs').setLevel(logging.ERROR)


def acquire_data(year, season, season_col, name_col):
    """
    Obtain NCAA basketball player statistics using the sportsipy API to pull
    the data from sports-reference.com
    Args:
        year: (int), Required: Year used to get players from API that played that year
        season (String), Required: String of last season year range to filter player data on
        season_col (String), Required: Name of the newly created season column
        name_col (String), Required: Name of newly created name column
    Returns:
        df: (Pandas DataFrame): Raw, uncleaned data from API converted to DataFrame
    """
    try:
        # Initialize variables
        df = pd.DataFrame()

        # Loop through all the NCAA men's basketball teams competing in 2021
        for team in Teams(year):
            # Loop through all the players on the currently selected team's roster
            for player in team.roster.players:

                # Obtain the full player statistics dataframe
                player_df = player.dataframe

                # If the player played in the recent season, get that player's data
                if season in player_df.index:

                    # Reset the index which is currently the season
                    player_df = player_df.rename_axis(season_col).reset_index()

                    # Add a column for player name
                    player_df[name_col] = player.name

                    # Append the player's stats to the existing players dataframe
                    df = df.append(player_df, ignore_index=True)

        # Convert heights to inches to avoid formatting issues when saving to Excel
        df['height'] = df['height'].fillna(0)
        df['height'] = df['height'].str.split('-').str[0].fillna(0).apply(int)*12 + df['height'].str.split('-').str[1].fillna(0).apply(int)
        logger.info('Height column converted to inches.')

        # Raise a warning if data was not pulled during API call process
        if df.shape[0] == 0:
            logger.warning('Obtained dataframe contains zero rows.')
        else:
            logger.info('Data obtained with number of rows: %s', df.shape[0])

        return df

    except requests.exceptions.ConnectionError:
        logger.error('A connection error occurred. Please check that you are connected to the internet and that sports-reference.com is not down.')


def upload_data(df, filepath):
    """
    Upload the acquired data to an S3 Bucket or download it to a local path
    Args:
        df: (Pandas DataFrame), Required: Raw, uncleaned data from API
        filepath: (String), Required: Location to save data
    Returns:
        None
    """

    # Try to upload to path, catch any exceptions that occur
    try:
        df.to_csv(filepath,index=False)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    except botocore.exceptions.PartialCredentialsError:
        logger.error('One environment variable is missing. Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    except botocore.exceptions.ConnectionError:
        logger.error('A connection was unable to be established. Please check your internet/connection.')
    except botocore.exceptions.ClientError:
        logger.error('An unexpected error occurred. Please try again.')
    except FileNotFoundError:
        logger.error('The file is not located in the local path /data/external/sports_ref.csv. Please download it from the API to that location.')
    except OSError:
        logger.error('The filepath %s to save to could not be found or accessed.',filepath)
    except AttributeError:
        logger.error('The DataFrame does not exist. Please check your data source location argument.')
    else:
        logger.info('Data uploaded to %s', filepath)
