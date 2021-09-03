import pytest
import pandas as pd
import numpy as np

from src.clean_featurize import clean_data

def test_clean_data():
    # Define input DataFrame
    df_in_values = [['james-wiseman','2020-21','memphis',400,83,400,100,20,40,np.nan,20],['evan-mobley','2020-21','southern-cal',440,84,220,200,40,80,2,22],
                    ['nick-nigro','2020-21','new-hampshire',0,'6-0',0,0,0,0,0,1000],['larry-bird','1967-68','indiana-state',754,'6-5',47,43,23,65,5,23]]

    df_in_columns = ['player_id','season','team_abbreviation','minutes_played','height','points','total_rebounds','assists','blocks','steals','turnovers']

    df_in = pd.DataFrame(df_in_values, columns=df_in_columns)

    # Define other test inputs
    season_in = '2020-21'
    season_col_in = 'season'
    year_col_in = 'year'
    max_years_in = 4
    year_mapping_in = {1:'Freshman',2:'Sophomore',3:'Junior'}
    min_minutes_in = 100
    team_col_in = 'team'
    na_fill_val_in = 0
    drop_columns_in = ['team_abbreviation']

    # Define true DataFrame
    df_true_values = [['james-wiseman','2020-21',400,83,400,100,20,40,0.,20,'Freshman','memphis'],['evan-mobley','2020-21',440,84,220,200,40,80,2,22,'Freshman','southern cal']]
    df_true_columns = ['player_id','season','minutes_played','height','points','total_rebounds','assists','blocks','steals','turnovers','year','team']
    df_true = pd.DataFrame(df_true_values, columns=df_true_columns)

    # Run test by calling function
    df_test = clean_data(df_in,season_in,season_col_in,year_col_in,max_years_in,year_mapping_in,min_minutes_in,team_col_in,na_fill_val_in,drop_columns_in)

    # Test that true and test are the same
    pd.testing.assert_frame_equal(df_test,df_true)

def test_clean_data_non_df():
    # Define input data that is not a dataframe
    df_in = 'I am not a dataframe'

    # Define other inputs
    season_in = '2020-21'
    season_col_in = 'season'
    year_col_in = 'year'
    max_years_in = 4
    year_mapping_in = {1:'Freshman',2:'Sophomore',3:'Junior'}
    min_minutes_in = 100
    team_col_in = 'team'
    na_fill_val_in = 0
    drop_columns_in = ['team_abbreviation']

    # Verify TypeError arises
    with pytest.raises(TypeError):
        clean_data(df_in,season_in,season_col_in,year_col_in,max_years_in,year_mapping_in,min_minutes_in,team_col_in,na_fill_val_in,drop_columns_in)

def test_clean_data_col_missing():
    # Define input dataframe with column with missing column name
    df_in = pd.DataFrame()

    # Define other test inputs
    season_in = '2020-21'
    season_col_in = 'season'
    year_col_in = 'year'
    max_years_in = 4
    year_mapping_in = {1:'Freshman',2:'Sophomore',3:'Junior'}
    min_minutes_in = 100
    team_col_in = 'team'
    na_fill_val_in = 0
    drop_columns_in = ['team_abbreviation']

    # Verify ValueError arises
    with pytest.raises(ValueError):
        clean_data(df_in,season_in,season_col_in,year_col_in,max_years_in,year_mapping_in,min_minutes_in,team_col_in,na_fill_val_in,drop_columns_in)
