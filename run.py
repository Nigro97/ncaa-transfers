import argparse
import logging
import logging.config

logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger(__name__)

import yaml
import pandas as pd

from src.api_getdata import acquire_data, upload_data
from src.results_db import create_db, ResultsManager
from src.clean_featurize import download_from_s3, clean_data, featurize
from src.model_pipeline import optimal_clusternum, test_cluster_stability, final_cluster_fit
from config.flaskconfig import SQLALCHEMY_DATABASE_URI


if __name__ == '__main__':

    # Add parsers for both creating a database and downloading raw data
    parser = argparse.ArgumentParser(description='Create database or get data')
    subparsers = parser.add_subparsers(dest='subparser_name')

    # Sub-parser for creating a database
    sb_create = subparsers.add_parser('create_db', description='Create database')
    sb_create.add_argument('--engine_string', default=SQLALCHEMY_DATABASE_URI,
                           help='SQLAlchemy connection URI for database.')

    # Sub-parser for downloading data to local or uploading to S3
    sb_download = subparsers.add_parser('get_data', description='Download data to local path or S3 bucket')
    sb_download.add_argument('--savepath', default='data/external/sports_ref.csv',
                           help='S3 or local filepath location to save data.')
    sb_download.add_argument('--source', default='local',
                           help='Location to obtain data for upload: Type "api" or "local"')

    # Sub-parser for cleaning data and running K-means clustering
    sb_model = subparsers.add_parser('get_clusters', description='Run K-means clustering to get player types')
    sb_model.add_argument('--loadpath', default='data/external/sports_ref.csv',
                           help='S3 or local path used to obtain raw data.')
    sb_model.add_argument('--savepath', default='data/sports_ref_clean.csv',
                           help='Local path to save cleaned data with cluster labels.')

    # Sub-parser for populating the database
    sb_populate = subparsers.add_parser('populate_db', description='Populate database with player data and types')
    sb_populate.add_argument('--engine_string', default=SQLALCHEMY_DATABASE_URI,
                           help='SQLAlchemy connection URI for database.')
    sb_populate.add_argument('--loadpath', default='data/sports_ref_clean.csv',
                           help='Local path to load cleaned data with cluster labels.')
    # Get all args
    args = parser.parse_args()
    sp_used = args.subparser_name

    # Open yaml file and get all variables
    with open('config/config.yaml', 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    logger.info('Configuration file loaded from config/config.yaml')

    # Get the YAML sections for each script
    config_run = config['run']
    config_data = config['api_getdata']
    config_clean = config['clean_featurize']
    config_model = config['model_pipeline']

    # Create database when create_db arg is input
    if sp_used == 'create_db':
        logger.debug('Attempting to create database.')
        create_db(args.engine_string)

    # Download data from API to local path or S3 bucket
    elif sp_used == 'get_data':
        # If source arg is api, download from API before saving data to path
        if args.source == 'api':
            logger.info('Getting data from API. Please wait. This may take 20 minutes.')
            upload_data(acquire_data(**config_data['acquire_data']),args.savepath)

        # If source arg is local, download from local before saving data to path
        elif args.source == 'local':
            try:
                df = pd.read_csv(config_run['raw_local'])
            except FileNotFoundError:
                logger.error('Data not found at local path %s',config_run['raw_local'])
            else:
                logger.info('Getting data from local path.')
                upload_data(df,args.savepath)

        # If source arg is not one of the two expected options, download from local and give warning
        else:
            try:
                df = pd.read_csv(config_run['raw_local'])
            except FileNotFoundError:
                logger.error('A proper data acquisition location was not specified and data was not found at local path %s',config_run['raw_local'])
            else:
                logger.warning('A proper data acquisition location was not specified, so data was uploaded from the local path: data/external/sports_ref.csv')
                upload_data(df,args.savepath)

    # Run full model pipeline starting from getting data from S3 bucket and ending with saving cleaned dataframe with cluster labels
    elif sp_used == 'get_clusters':
        # Download raw data from S3 bucket
        raw_df = download_from_s3(args.loadpath)

        # Clean data
        df = clean_data(raw_df,config_data['acquire_data']['season'],config_data['acquire_data']['season_col'],**config_clean['clean_data'])

        # Create features
        features = featurize(df,**config_clean['featurize'])

        # Generate plots and metrics showing optimal cluster parameters and stability of clusters
        optimal_clusternum(features,**config_model['kmeans_all'],**config_model['optimal_clusternum'])
        test_cluster_stability(features,**config_model['kmeans_all'],**config_model['test_cluster_stability'])

        # Get optimal cluster labels
        clusters = final_cluster_fit(features,**config_model['kmeans_all'],**config_model['final_cluster_fit'])

        # Save player data with cluster labels to local path
        try:
            clusters.to_csv(args.savepath,index=False)
        except OSError:
            logger.error('The filepath %s could not be found or accessed.',args.savepath)
        else:
            logger.info('Cleaned data with cluster labels saved to %s',args.savepath)

    # Populate database with player data and cluster labels
    elif sp_used == 'populate_db':
        # Read cleaned data from local path to save to database
        try:
            df = pd.read_csv(args.loadpath)
        except:
            logger.error('Data not found at load path %s',args.loadpath)
        else:
            logger.info('Cleaned data with cluster labels loaded from %s',args.loadpath)

            # initialize results manager to connect to database
            rm = ResultsManager(engine_string=args.engine_string)

            # loop through the rows in the dataframe, calling the add_player function to add that row to the dataframe each time
            logger.debug('Attempting to populate database.')
            for row in range(len(df)):
                rm.add_player(df.loc[row,'player_id'],df.loc[row,'name'],df.loc[row,'year'],df.loc[row,'position'],int(df.loc[row,'height']),int(df.loc[row,'weight']),
                    df.loc[row,'player_type'],df.loc[row,'team'],df.loc[row,'conference'],int(df.loc[row,'games_played']),int(df.loc[row,'games_started']),
                    round(df.loc[row,'field_goal_percentage'],2),round(df.loc[row,'three_point_percentage'],2),round(df.loc[row,'free_throw_percentage'],2),int(df.loc[row,'points']),
                    round(df.loc[row,'ppm'],2),int(df.loc[row,'assists']),round(df.loc[row,'apm'],2),round(df.loc[row,'assist_percentage'],2),int(df.loc[row,'total_rebounds']),round(df.loc[row,'rpm'],2),
                    round(df.loc[row,'total_rebound_percentage'],2),int(df.loc[row,'blocks']),round(df.loc[row,'bpm'],2),round(df.loc[row,'block_percentage'],2),int(df.loc[row,'steals']),
                    round(df.loc[row,'spm'],2),round(df.loc[row,'steal_percentage'],2),int(df.loc[row,'turnovers']),round(df.loc[row,'tpm'],2),round(df.loc[row,'turnover_percentage'],2),
                    df.loc[row,'usage_percentage'],df.loc[row,'player_efficiency_rating'])

            # close the results manager when completed populating the database
            rm.close()
            logger.info('%i rows of player data populated in database.', row+1)

    else:
        parser.print_help()
