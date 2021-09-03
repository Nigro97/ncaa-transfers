import pytest
import pandas as pd
import numpy as np

from src.clean_featurize import featurize

def test_featurize():
    # Define input DataFrame
    df_in_values = [['james-wiseman','2020-21','Freshman','memphis',400,83,400,100,20,40,0,20],['evan-mobley','2020-21','Freshman','southern cal',440,84,220,110,44,88,0,22]]

    df_in_columns = ['player_id','season','year','team','minutes_played','height','points','total_rebounds','assists','blocks','steals','turnovers']

    df_in = pd.DataFrame(df_in_values, columns=df_in_columns)

    # Define other test inputs
    ppm_col_in = 'ppm'
    apm_col_in = 'apm'
    rpm_col_in = 'rpm'
    bpm_col_in = 'bpm'
    spm_col_in = 'spm'
    tpm_col_in = 'tpm'

    # Define true DataFrame
    df_true_values = [['james-wiseman','2020-21','Freshman','memphis',400,83,400,100,20,40,0,20,1,.05,.25,.1,0.,.05],['evan-mobley','2020-21','Freshman','southern cal',440,84,220,110,44,88,0,22,.5,.1,.25,.2,0.,.05]]
    df_true_columns = ['player_id','season','year','team','minutes_played','height','points','total_rebounds','assists','blocks','steals','turnovers','ppm','apm','rpm','bpm','spm','tpm']
    df_true = pd.DataFrame(df_true_values, columns=df_true_columns)

    # Run test by calling function
    df_test = featurize(df_in,ppm_col_in,apm_col_in,rpm_col_in,bpm_col_in,spm_col_in,tpm_col_in)

    # Test that true and test are the same
    pd.testing.assert_frame_equal(df_test,df_true)

def test_featurize_non_df():
    # Define input data that is not a dataframe
    df_in = 'I am not a dataframe'

    # Define other inputs
    ppm_col_in = 'ppm'
    apm_col_in = 'apm'
    rpm_col_in = 'rpm'
    bpm_col_in = 'bpm'
    spm_col_in = 'spm'
    tpm_col_in = 'tpm'

    # Verify TypeError arises
    with pytest.raises(TypeError):
        df_test = featurize(df_in,ppm_col_in,apm_col_in,rpm_col_in,bpm_col_in,spm_col_in,tpm_col_in)
