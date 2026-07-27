import requests
import pandas as pd
import numpy as np
import re

def clean_responses(responses_df, question_df):
    """
    Extracts columns with questions from responses_df, removes rows with all
    NaN values in those columns, and resets the index.
    
    Parameters:
    responses_df (pd.DataFrame): DataFrame containing survey responses.
    question_df (pd.DataFrame): DataFrame containing questions, with a 
                                'question_id' column.
    
    Returns:
    pd.DataFrame: Cleaned DataFrame with rows containing all NaN values removed 
                  and index reset.
    """
    # Extract only columns with questions
    df = responses_df.loc[:, question_df['question_id'].tolist()]

    # Find rows with all NaN values in question columns
    nan_mask = df.isna()
    keep_mask = np.array(nan_mask.sum(axis=1) < len(df.columns))

    # Filter responses_df based on keep_mask and reset index
    responses_df = responses_df.loc[keep_mask, :].reset_index(drop=True)
    
    return responses_df


def export_survey_responses(base_url, token, survey_id):
    """
    Initiates the export of survey responses from Qualtrics.

    Args:
        base_url (str): The base URL for the Qualtrics API.
        access_token (str): The bearer access token for API authorization.
        survey_id (str): The unique ID of the survey whose responses are to be exported.

    Returns:
        dict: A JSON-formatted response containing the export details, such as progress and file ID.
    """
    # Set the survey export URL
    survey_export_url = '{0}/API/v3/surveys/{1}/export-responses'.format(base_url, survey_id)
    # Pull the survey data
    response = requests.post(survey_export_url, 
                             headers={"Content-Type": "application/json",
                                      "Authorization": "Bearer " + token},
                             data='{"format": "json", "compress": false}')
    # Convert the data into a more readable format
    response = response.json()    
    return response


def wait_for_export_completion(base_url, token, survey_id, export_progress_id):
    """
    Waits for the survey response export to complete by checking its progress.

    Args:
        base_url (str): The base URL for the Qualtrics API.
        token (str): The API token used for authorization.
        survey_id (str): The ID of the survey being exported.
        export_progress_id (str): The progress ID of the ongoing export.

    Returns:
        str: The file ID (file_id) when the export is complete.
    """
    # Initialize the file ID to empty
    file_id = ""
    
    # Loop until the export is complete and the file ID is available
    while len(file_id) == 0:
        # Check the progress of the export
        response_export_progress = get_response_export_progress(
            base_url, 
            token, 
            survey_id, 
            export_progress_id)

        # Check if the export is 100% complete
        if response_export_progress.get('result').get('percentComplete') == 100:
            # Check if the status is 'complete'
            if response_export_progress.get('result').get('status') == 'complete':
                # Get the file ID
                file_id = response_export_progress.get('result').get('fileId')
            else:
                print("Status: " + response_export_progress.get('result').get('status'))
    
    return file_id


def get_response_export_progress(base_url, access_token, survey_id, export_progress_id):
    """
    Checks the progress of an ongoing survey response export.

    Args:
        base_url (str): The base URL for the Qualtrics API.
        access_token (str): The bearer access token for API authorization.
        survey_id (str): The unique ID of the survey whose responses are being 
                         exported.
        export_progress_id (str): The unique ID representing the current export 
                                  progress.

    Returns:
        dict: A JSON-formatted response indicating the progress status and completion percentage.
    """
    export_progress_url = '{0}/API/v3/surveys/{1}/export-responses/{2}'.format(base_url, survey_id, export_progress_id)
    # Pull the survey data
    response = requests.get(export_progress_url, 
                            headers={"Content-Type": "application/json",
                                     "Authorization": "Bearer " + access_token})
    # Convert the data into a more readable format
    response = response.json()    
    return response


def get_survey_responses(base_url, access_token, survey_id, file_id):
    """
    Downloads the survey responses after the export process is complete.

    Args:
        base_url (str): The base URL for the Qualtrics API.
        access_token (str): The bearer access token for API authorization.
        survey_id (str): The unique ID of the survey whose responses are to be 
                        downloaded.
        file_id (str): The file ID representing the exported survey responses.

    Returns:
        requests.Response: The HTTP response containing the survey responses file.
    """
    file_download_url = '{0}/API/v3/surveys/{1}/export-responses/{2}/file'.format(base_url, survey_id, file_id)
    # Pull the survey data
    response = requests.get(file_download_url, 
                            headers={"Content-Type": "application/json",
                                     "Authorization": "Bearer " + access_token})
    return response


def extract_and_organize_responses(survey_responses):
    """
    Extracts and organizes survey responses from the JSON response.

    Args:
        survey_responses (requests.Response): The response object from the 
                                              survey responses export.

    Returns:
        pd.DataFrame or None: A DataFrame containing the organized responses, 
                              or None if no responses are available.
    """
    # Convert the response content to JSON
    survey_responses_json = survey_responses.json()
    
    # Extract the list of responses
    responses = survey_responses_json.get('responses', [])
    
    if len(responses) > 0:
        # Organize the responses using qa's organize_responses function
        responses_df = organize_responses(responses)
        return responses_df
    else:
        print('There is no data')
        return None
    

def filter_preview_responses(responses_df):
    """
    Filters out survey preview responses from the responses DataFrame and 
    resets the index.
    
    Parameters:
    responses_df (pd.DataFrame): DataFrame containing survey responses with a 
                                'distributionChannel' column.
    
    Returns:
    pd.DataFrame: Filtered DataFrame with preview responses removed and index reset.
    """
    # Do not keep survey preview responses
    keep_mask = np.array(responses_df['distributionChannel'] != 'preview')
    filtered_df = responses_df.loc[keep_mask, :].reset_index(drop=True)
    
    return filtered_df


def organize_responses(responses):
    """
    Organize survey responses into a structured DataFrame.
    
    Args:
        responses (list): List of survey response data in JSON format.
    
    Returns:
        pd.DataFrame: A DataFrame containing the organized responses.
    """
    responses_df = pd.DataFrame()

    for response in responses:
        # Extract the current response and normalize it into a DataFrame
        temp_df = pd.json_normalize(response.get('values'))
        if len(responses_df) == 0:
            responses_df = temp_df
        else:
            # Concatenate the responses into the DataFrame
            responses_df = pd.concat([responses_df, temp_df])
    
    responses_df = responses_df.reset_index(drop=True)
    
    # Reorder the columns: first non-question columns, then question columns
    column_names = responses_df.columns
    question_columns = [col for col in column_names if col.startswith('QID')]
    non_question_columns = list(set(column_names) - set(question_columns))
    
    non_question_df = responses_df.loc[:, np.isin(column_names, non_question_columns)]

    # Prepare to order question columns by number, sub-question, and loop number
    question_number = []
    sub_question_number = []
    loop_number = []

    for question in question_columns:
        # Split the column name into parts (e.g., 'QID1_1_TEXT' becomes ['QID1', '1', 'TEXT'])
        split_column_name = re.split('_|#', question)
        
        # Find the index of the 'QID' part of the split
        qid_index = [i for i in range(len(split_column_name)) if 'QID' in split_column_name[i]]
        max_index = len(split_column_name) - 1

        # Determine if it's a loop question
        if qid_index[0] == 0:
            loop_number.append(0)
        elif qid_index[0] == 1:
            loop_number.append(int(split_column_name[0]))
        else:
            print('Issues with ' + question)
            break

        # Extract the numeric part of the QID (e.g., 'QID1' becomes ['QID', '1'])
        qid_numeric_parts = re.split('QID', split_column_name[qid_index[0]])
        question_number.append(int(qid_numeric_parts[1]))

        # Handle sub-questions
        if max_index > qid_index[0]:
            if split_column_name[qid_index[0] + 1].isnumeric():
                sub_question_number.append(int(split_column_name[qid_index[0] + 1]))
            else:
                sub_question_number.append(0)
        else:
            sub_question_number.append(0)
    
    # Create a DataFrame to sort the questions
    question_id_dict = {
        'question_column': question_columns,
        'question_number': question_number,
        'sub_question_number': sub_question_number,
        'loop_number': loop_number
    }
    question_id_df = pd.DataFrame(question_id_dict)
    question_id_df = question_id_df.sort_values(
        by=['question_number', 'sub_question_number', 'loop_number'],
        ascending=[True, True, True]
    )
    # Extract the question columns in the new order
    question_df_sorted = responses_df.loc[:, question_id_df['question_column']]
    
    # Concatenate non-question and question columns
    final_results_df = pd.concat([non_question_df, question_df_sorted], axis=1)
    
    return final_results_df

