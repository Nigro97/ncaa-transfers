import logging
import requests

import pandas as pd
import botocore

logger = logging.getLogger(__name__)

logging.getLogger('botocore').setLevel(logging.ERROR)
logging.getLogger('s3transfer').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('asyncio').setLevel(logging.ERROR)
logging.getLogger('aiobotocore').setLevel(logging.ERROR)
logging.getLogger('s3fs').setLevel(logging.ERROR)


def download_from_s3(path):
    """
    Download the data from an S3 Bucket or a local path
    Args:
        path: (String), Required: S3 Bucket path or local path containing raw data
    Returns:
        df: (Pandas DataFrame): Uncleaned data from source put in DataFrame form
    """
    # Try to download data from S3 while catching all errors
    try:
        df = pd.read_csv(path)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    except botocore.exceptions.PartialCredentialsError:
        logger.error('One environment variable is missing. Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    except botocore.exceptions.ConnectionError:
        logger.error('A connection was unable to be established. Please check your internet/connection.')
    except botocore.exceptions.ClientError:
        logger.error('An unexpected error occurred. Please try again.')
    except ConnectionError:
        logger.error('A connection error occurred. Please check that you are connected to the internet.')
    else:

        # Return raw data in DataFrame format
        logger.info('Data downloaded from %s', path)
        return df


def clean_data(df,season,season_col,year_col,max_years,year_mapping,min_minutes,team_col,na_fill_val,drop_columns):
    """
    Clean the data contained in the dataframe to be used for feature engineering and modeling
    by filtering to get deisred subset of players/years and
    Args:
        df: (Pandas DataFrame), Required: Uncleaned data from source
        season (String), Required: String of last season year range to filter player data on
        season_col (String), Required: Name of the season column created  during the API data download
        year_col (String), Required: Name of the newly created year column
        max_years (int), Required: Number of years player to filter on to remove Seniors who are graduating
        year_mapping (dict), Required: Map of number of years played to college class
        min_minutes (int), Required: Minimum minutes needed for a player to play to be used in clustering
        team_col (String), Required: Name of newly created team name column
        na_fill_val (int), Required: Value used to fill in NAs in percentage columns
        drop_columns (list of Strings), Required: Columns dropped during the cleaning process
    Returns:
        df: (Pandas DataFrame): Cleaned data
    """
    # Ensure df is a DataFrame
    if not isinstance(df, pd.DataFrame):
        logger.error('Provided argument `df` is not a Pandas DataFrame object')
        raise TypeError('Provided argument `df` is not a Pandas DataFrame object')

    # Check to make sure the season column exists
    if season_col not in df.columns:
        logger.error('Provided argument `df` does not have a column named %s', season_col)
        raise ValueError('Provided argument `df` does not contain the specified column.')

    # Check to make sure the year column exists
    if season_col not in df.columns:
        logger.error('Provided argument `df` does not have a column named %s', year_col)
        raise ValueError('Provided argument `df` does not contain the specified column.')

    # Get the number of seasons a player has played for
    num_years = df.groupby('player_id').agg('count').iloc[:,0]
    num_years.rename(year_col, axis='columns', inplace=True)

    # Add the number of years played as a column
    df = df.merge(num_years,on='player_id',how='left')
    logger.info('New `number of years played for` column created.')

    # Filter seasons by 2020-21 season only. We do not care about previous season stats
    df = df[df[season_col]==season]
    logger.info('Filtered to include 2020-21 season stats only. %i players played total.', len(df))

    # Filter by players that have less than 4 seasons since having 4 seasons means a players' eligibility has been used up
    df = df[df[year_col]<max_years]
    df[year_col] = df[year_col].map(year_mapping)
    logger.info('Filtered on players with less than 4 years of experience. %i players remain.', len(df))

    # Remove the dashes from team names for a better display
    df[team_col] = df['team_abbreviation'].str.replace('-',' ')

    # Filter players with more than 100 minutes played to have enough stats to draw conclusions from that are stable
    df = df[df['minutes_played']>min_minutes]
    logger.info('Filtered on players with more than 100 minutes played. %i players remain.', len(df))

    # Drop unneeded columns
    df.drop(drop_columns,axis=1,inplace=True)
    # Fill some percentage column values with 0 that have NAs due to no attempts
    df.fillna(na_fill_val,inplace=True)
    # Reset index now at end of cleaning
    df.reset_index(drop=True,inplace=True)
    logger.info('Completed dataframe cleaning.')
    return df


def featurize(df,ppm_col,apm_col,rpm_col,bpm_col,spm_col,tpm_col):
    """
    Engineer features to be used in modeling by calculating major statistics per minute
    Args:
        df: (Pandas DataFrame), Required: Cleaned data containing player statistics
        ppm_col (String), Required: Column name for the newly created points per minute column
        apm_col (String), Required: Column name for the newly created assists per minute column
        rpm_col (String), Required: Column name for the newly created rebounds per minute column
        bpm_col (String), Required: Column name for the newly created blocks per minute column
        spm_col (String), Required: Column name for the newly created steals per minute column
        tpm_col (String), Required: Column name for the newly created turnovers per minute column
    Returns:
        df: (Pandas DataFrame): Player statistics with new columns of engineered features
    """
    # Ensure df is a DataFrame
    if not isinstance(df, pd.DataFrame):
        logger.error('Provided argument `df` is not a Pandas DataFrame object')
        raise TypeError('Provided argument `df` is not a Pandas DataFrame object')

    # Create columns to calculate stats per minute
    df[ppm_col] = df['points']/df['minutes_played']
    df[apm_col] = df['assists']/df['minutes_played']
    df[rpm_col] = df['total_rebounds']/df['minutes_played']
    df[bpm_col] = df['blocks']/df['minutes_played']
    df[spm_col] = df['steals']/df['minutes_played']
    df[tpm_col] = df['turnovers']/df['minutes_played']

    logger.info('New features for statistics per minute calculated.')
    return df
