# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 10:17:57 2024

@author: kieranmartin
"""
import pandas as pd
import numpy as np
import src.qual_api as qa
from src.utils import (
    QUALTRICS_CREDS,
    get_token
)

# Extract client ID, secret, and data center from credentials
client_id = QUALTRICS_CREDS.get('ID')
client_secret = QUALTRICS_CREDS.get('Secret')
data_center = QUALTRICS_CREDS.get('DataCenter')
base_url = f'https://{data_center}.qualtrics.com'

# Define survey name and set up parameters for token request
survey_name = "Spring 2024 COPA People's Academy: Post-Participation Survey"
grant_type = 'client_credentials'
scope = 'read:surveys read:survey_responses'
data = qa.return_kwargs_as_dict(grant_type=grant_type, scope=scope)

# Get the bearer token
bearer_token_response = get_token(base_url, client_id, client_secret, data)
token = bearer_token_response.get("access_token")

# Retrieve the list of surveys and find the survey ID
survey_list_df = qa.get_survey_list(base_url, token)
survey_id = qa.get_survey_id_by_name(survey_list_df, survey_name)

# Export survey responses and track the progress
response_export = qa.export_survey_responses(base_url, token, survey_id)
export_progress_id = response_export.get('result').get('progressId')

# Wait for export to complete and retrieve file ID for responses
file_id = qa.wait_for_export_completion(base_url, token, survey_id, export_progress_id)

# Download and process the survey responses
survey_responses = qa.get_survey_responses(base_url, token, survey_id, file_id)
responses_df = qa.extract_and_organize_responses(survey_responses)
responses_df = qa.filter_preview_responses(responses_df)

# Retrieve survey questions and map them to response columns
survey_questions = qa.get_survey_questions(base_url, token, survey_id).get('result').get('questions')
question_df, question_values_df = qa.extract_column_data_types(survey_questions, responses_df, base_url, token, survey_id)
question_df = qa.create_data_type_dictionary(question_df, question_values_df)

# Clean responses and retain only question columns
responses_df = qa.clean_responses(responses_df, question_df)
df = responses_df.loc[:, question_df['question_id'].tolist()]

# Identify rows with all NaN values to filter them out
nan_mask = df.isna()
keep_mask = np.array(nan_mask.sum(axis=1) < len(df.columns)) # type: ignore
df = df.loc[keep_mask].reset_index(drop=True)

###############################################################################
def calculate_missing_data_stats(df):
    """
    Calculate statistics on missing and present data for each column in a DataFrame.

    This function calculates the number and fraction of missing and present data points 
    for each column in the provided DataFrame and returns a summary DataFrame with 
    these metrics.

    Parameters:
    ----------
    df : pd.DataFrame
        The input DataFrame containing data for which missing and present data statistics 
        will be calculated.

    Returns:
    -------
    pd.DataFrame
        A DataFrame summarizing missing and present data for each column, including:
        - question_id: Column names from the input DataFrame.
        - MissingDataN: Number of missing values in each column.
        - PresentDataN: Number of non-missing values in each column.
        - MissingDataFrc: Fraction of missing values in each column.
        - PresentDataFrc: Fraction of non-missing values in each column.
        
    Example:
    -------
    >>> missing_text_df = calculate_missing_data_stats(df)
    """
    
    # Calculate the number of missing and present values per column
    nan_mask = df.isna()
    missing_data = nan_mask.sum(axis=0).tolist()
    present_data = len(df) - np.array(missing_data)
    
    # Calculate the fraction of missing and present data
    missing_data_fraction = np.array(missing_data) / len(df)
    present_data_fraction = 1 - missing_data_fraction
    
    # Create the summary DataFrame
    missing_text_df = {
        'question_id': df.columns,
        "MissingDataN": missing_data,
        "PresentDataN": present_data,
        "MissingDataFrc": missing_data_fraction,
        "PresentDataFrc": present_data_fraction
    }
    
    return pd.DataFrame(missing_text_df)

missing_text_df = calculate_missing_data_stats(df)

free_text_columns = question_df.question_id[np.array(question_df.data_type == 'FreeText')]

# Grab the missing data for the text
mask_missing_text_df = np.array(np.isin(missing_text_df['question_id'], list(free_text_columns)))
mask_missing_text_df = missing_text_df.loc[mask_missing_text_df, :]

print(mask_missing_text_df)
