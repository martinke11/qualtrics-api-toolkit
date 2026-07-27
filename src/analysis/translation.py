#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 12:35:12 2023

@author: kieranmartin
"""
import pandas as pd
import numpy as np
import re
from googletrans import Translator
import time
import emoji
import warnings
import httpx
import nltk
# nltk.download('all') # nltk.download('vader_lexicon')
from textblob import TextBlob
import src.qual_api as qa
from src.utils import (
    QUALTRICS_CREDS,
    get_token
)

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
warnings.simplefilter(action='ignore', category=pd.errors.DtypeWarning)
pd.options.mode.chained_assignment = None 

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
free_text_columns = question_df.question_id[np.array(question_df.data_type == 'FreeText')]
free_text_columns = free_text_columns[~free_text_columns.str.contains('TEXT_')]

# Create text_df and use for translation or clean and process df to use for 
# translation:
text_df = df[free_text_columns]

def process_text_columns(df, free_text_cols):
    """ Process specified text columns in a dataframe.

    Parameters:
    -----------
    df : DataFrame
        The dataframe to process.
    free_text_cols : Series
        Series containing the names of the columns to process.
    """
    # Identify columns in df that are also in free_text_cols
    cols_to_process = df.columns.intersection(free_text_cols)

    for col in cols_to_process:
        # Convert to string
        df[col] = df[col].astype(str)
        # Replace 'N/A' and 'nan' with NaN
        df[col] = df[col].replace(r'N/A', np.nan, regex=True).replace(r'nan', np.nan, regex=True)

        # Replace new lines with space and whitespace strings with NaN
        df[col] = df[col].replace(r'\n', ' ', regex=True).replace(r'^\s*$', np.nan, regex=True)

        # Convert to lowercase and remove commas and special characters
        df[col] = df[col].apply(lambda x: re.sub(r'[^\w\s]', '', x.lower()) if pd.notnull(x) else x)
        
    if df.equals(text_df):
        # Drop columns that are all null only if df is not equal to text_df
        df.dropna(axis=1, how='all', inplace=True)

    return df

# Can clean either full df or just text_df depending on what function
# will be run below
text_df = process_text_columns(text_df, free_text_columns)
df = process_text_columns(df, free_text_columns)

# Every data set will have some unique cleaning that must be done. That can
# go here: 
#text_df.replace('Deutschland', 'Germany', inplace=True)


def remove_emojis(df):
    """ Function to remove emojis from a dataframe
    Parameters:
        -----------
        df (dataframe): dataframe including any columns
    """
    # get string columns
    non_numeric_columns = df.convert_dtypes().select_dtypes("string")
    non_numeric_columns = list(non_numeric_columns.columns)
    
    # remove emojis from each string column
    for col in non_numeric_columns:
        df[col] = df[col].apply(
            lambda s: emoji.replace_emoji(s, '')
            if pd.notnull(s) and s != "" and s != "\n" else s)
    return df

# Uncomment below function to remove emojis from text
# text_df = remove_emojis(text_df)
# df = remove_emojis(df)

######################## TRANSLATION ########################
def translate_seperate_text_df(df, col, translator):
    """
    Helper function to translate a specified column in a DataFrame.

    This function translates the specified column in `df` and creates new columns for the 
    translated text and any errors encountered during translation. For each original column 
    in `text_df`, a corresponding translated column and an error column are added. This 
    function is suitable for testing or comparing translation results as it does not map 
    back to the original `df`.

    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame including the column to be translated.
    col : str
        The name of the specific column to be translated.
    translator : Translator object
        An object capable of performing translations, such as `googletrans.Translator`.

    Returns:
    --------
    pd.DataFrame
        A DataFrame with the new translated column and error column added.

    """
    translated_col_name = col + '_translated'
    error_col_name = col + '_error'
    df[translated_col_name] = pd.NA  # Initialize new column with NA
    df[error_col_name] = pd.NA  # Initialize error column

    for index, row in df.iterrows():
        if pd.notnull(row[col]) and row[col].strip(): 
            try:
                translated_text = translator.translate(row[col], src='auto', dest='ja').text
                df.loc[index, translated_col_name] = translated_text
                time.sleep(0.5)
            except Exception as e:
                print("ERROR WITH:", row[col])
                df.loc[index, translated_col_name] = row[col]
                df.loc[index, error_col_name] = 'error'
        else:
            df.loc[index, translated_col_name] = row[col]
    
    # Reorder columns so that translated column is right after the original column
    col_index = df.columns.get_loc(col)
    reordered_cols = df.columns.to_list()[:col_index + 1] + [translated_col_name, error_col_name] + df.columns.to_list()[col_index + 1:-2]
    df = df[reordered_cols]

    return df


timeout = httpx.Timeout(120) 
translator = Translator(timeout=timeout, raise_exception=True)

translated_data_full = text_df.copy()
for col in free_text_columns:
    print(col, ": there are", translated_data_full[col].count(), "non null entries to translate.")
    translated_data_full = translate_seperate_text_df(translated_data_full, col, translator)
    print("Finished", col)
    time.sleep(5)
    

def translate_replace_full_df(df, col, translator):
    """
    Helper function to translate a specified column in a DataFrame in-place.

    This function translates all entries in the specified column (`col`) within `df`
    that match the free text fields and replaces each entry directly in the original DataFrame. 
    This approach does not create separate columns for comparison; instead, the translated 
    text replaces the original content.

    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame including the column to be translated.
    col : str
        The name of the specific column to be translated.
    translator : Translator object
        An object capable of performing translations, such as `googletrans.Translator`.

    Returns:
    --------
    pd.DataFrame
        The original DataFrame with translations applied directly to the specified column.

    """
    for index, row in df.iterrows():
        if pd.notnull(row[col]) and row[col].strip():
            try:
                translated_text = translator.translate(row[col], src='auto', dest='en').text
                df.at[index, col] = translated_text
                time.sleep(0.5)
            except Exception as e:
                print("ERROR WITH:", row[col])
                # Optionally, handle error case here, e.g., leave the text as is or mark it
                # df.at[index, col] = 'Translation Error'  # or leave it as is
    return df

timeout = httpx.Timeout(120) 
translator = Translator(timeout=timeout, raise_exception=True)

for col in free_text_columns:
    print(col, ": there are", df[col].count(), "non null entries to translate.")
    df = translate_replace_full_df(df, col, translator)
    print("Finished", col)
    time.sleep(5)
 
# Code for the output csv or excel:
# df.to_csv('full_translation_athlete_survey.csv', index = False)
