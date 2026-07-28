import requests
import pandas as pd
import numpy as np
import re

def strip_html(data):
    """
    Remove HTML tags from the input data, which may be a string, list, or dictionary.
    
    Args:
        data (str, list, or dict): The data from which HTML tags should be stripped.
    
    Returns:
        The same data structure with HTML tags removed from strings.
    """
    html_pattern = re.compile(r'<[^>]*>')
    if isinstance(data, str):
        return html_pattern.sub('', data)
    elif isinstance(data, dict):
        return {k: strip_html(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [strip_html(item) for item in data]
    else:
        return data

def is_numeric(current_question):
    """
    Checks if a question should be treated as numeric based on type or 
    validation settings.
    """
    question_type = current_question.get('questionType', {}).get('type')
    
    # Treat Rank Order and Slider questions as numeric by default
    if question_type in ['RO', 'Slider']:
        return True
    
    # Check for validation settings indicating numeric input
    if 'validation' in current_question:
        current_validation = current_question.get('validation')
        if 'type' in current_validation and current_validation.get('type') == 'ValidNumber':
            return True
    
    return False

def create_question_dataframes(
        question_id_list, 
        question_name_list, 
        question_text_list, 
        question_type_list, 
        question_selector_list, 
        is_numeric_list, 
        long_text_id_list, 
        question_value_list, 
        answer_id_list, 
        keep_question_list
):
    """
    Creates the final dataframes for question data and question values.
    """
    question_df = pd.DataFrame({
        "question_id": np.array(question_id_list)[np.array(keep_question_list)],
        "question_name": np.array(question_name_list)[np.array(keep_question_list)],
        "question_text": np.array(question_text_list)[np.array(keep_question_list)],
        "question_type": np.array(question_type_list)[np.array(keep_question_list)],
        "question_selector": np.array(question_selector_list)[np.array(keep_question_list)],
        "is_numeric": np.array(is_numeric_list)[np.array(keep_question_list)]
    })
    
    question_values_df = pd.DataFrame({
        "question_id": long_text_id_list,
        "question_value": question_value_list,
        "answer_id": answer_id_list
    })
    
    return question_df, question_values_df


def create_data_type_dictionary(question_df, question_values_df):
    """
    Creates a dictionary of data types for the questions and adds the 
    corresponding data types to the question DataFrame.
    
    Args:
        question_df (pd.DataFrame): DataFrame containing the questions' metadata.
        question_values_df (pd.DataFrame): DataFrame containing the question 
                                            values and answer IDs.
    
    Returns:
        pd.DataFrame: The updated question DataFrame with an added 'DataType' column.
    """    
    # Get lists of the Free Text columns
    mask = (
        np.array(question_df['question_type'] == 'TE')
        & np.array(question_df['is_numeric'] is False)
    )
    free_text_columns = set(question_df['question_id'][mask])

    # FileUpload columns
    file_upload_columns = set(
        question_df['question_id'][
            question_df['question_type'] == 'FileUpload'
        ]
    )

    # Get list of Meta columns (categorical but without predefined categories)
    meta_columns = set(
        question_df['question_id'][
            question_df['question_type'] == 'Meta'
        ]
    )

    # Get lists of the Draw columns (often signatures)
    draw_columns = set(
        question_df['question_id'][
            question_df['question_type'] == 'Draw'
        ]
    )

    # Frequency Plots (Multiple Choice questions)
    multiple_choice_columns = set(question_values_df['question_id'])

    # Timing columns (tracks page times)
    timing_columns = set(
        question_df['question_id'][
            question_df['question_type'] == 'Timing'
        ]
    )

    # Date columns
    date_columns = set(
        question_df['question_id'][
            question_df['question_type'] == 'SBS'
        ]
    )

    # Rank Order columns
    rank_order_columns = set(
        question_df['question_id'][
            question_df['question_type'] == 'RO'
        ]
    )

    # Group columns for questions and responses
    group_columns = set(
        question_df['question_id'][
            question_df['question_type'] == 'PGR'
        ]
    )

    # Get the numeric columns
    # numeric_columns = set(question_df['question_id'][question_df['is_numeric']])
    numeric_columns = set(
        question_df['question_id'][
            question_df['is_numeric']
            | question_df['question_id'].isin(rank_order_columns)
        ]
    )
    
    # Create a dictionary of all the different column types
    column_data_types = {
        'MultipleChoice': list(multiple_choice_columns),
        'Numeric': list(numeric_columns),
        'FreeText': list(free_text_columns),
        'RankOrder': list(rank_order_columns),
        'FileUpload': list(file_upload_columns),
        'Group': list(group_columns),
        'MetaData': list(meta_columns),
        'Draw': list(draw_columns),
        'Timing': list(timing_columns),
        'Dates': list(date_columns)
    }
    
    # Determine the data type for each question
    data_type = []

    for question_id, question_type, question_selector in zip(
            question_df['question_id'],
            question_df['question_type'],
            question_df['question_selector'],
    ):  
        # Prioritize Rank Order
        if question_id in column_data_types.get('RankOrder', []):
            data_type.append('Numeric')
        elif question_id in column_data_types.get('Numeric', []):
            data_type.append('Numeric')
        elif question_id in column_data_types.get('MultipleChoice', []):
            data_type.append('MultipleChoice')
        elif question_id in column_data_types.get('FreeText', []):
            data_type.append('FreeText')
        elif question_id in column_data_types.get('FileUpload', []):
            data_type.append('FileUpload')
        elif question_id in column_data_types.get('Group', []):
            data_type.append('Group')
        elif question_id in column_data_types.get('MetaData', []):
            data_type.append('MetaData')
        elif question_id in column_data_types.get('Draw', []):
            data_type.append('Draw')
        elif question_id in column_data_types.get('Timing', []):
            data_type.append('Timing')
        elif question_id in column_data_types.get('Dates', []):
            data_type.append('Dates')
        elif question_type == 'Matrix' and question_selector == 'Likert':
            data_type.append('MultipleChoice')  # Assign 'MatrixLikert' type for Matrix-Likert questions
        else:
            data_type.append('Unknown')  # Default data type

    # Add the determined data types to the question DataFrame
    question_df['data_type'] = data_type
    return question_df


def reorder_question_df_with_normalized_ids(question_df, blocks_df):
    """
    Reorders the question_df DataFrame to match the Question ID order in blocks_df,
    creating a separate column for normalized Question IDs.

    Args:
        question_df (pd.DataFrame): DataFrame containing question metadata.
        blocks_df (pd.DataFrame): DataFrame with ordered Block Names and Question IDs.

    Returns:
        pd.DataFrame: A reordered question_df DataFrame.
    """
    # Add a separate column for normalized IDs
    question_df['normalized_id'] = question_df['question_id'].str.extract(r'^(QID\d+)')
    
    # Merge blocks_df with question_df based on the normalized ID
    merged_df = blocks_df.merge(
        question_df, 
        how='left', 
        left_on='Question ID', 
        right_on='normalized_id'
    )
    
    # Drop unnecessary columns and reorder
    reordered_question_df = merged_df.drop(columns=['normalized_id']).reset_index(drop=True)

    return reordered_question_df

def subset_by_date_range(responses_df, start_date, end_date):
    """
    Subset the responses DataFrame based on a specified date range.

    This function filters the `responses_df` DataFrame to include only rows 
    where the 'recordedDate' column falls within the specified `start_date` and 
    `end_date` range. The 'recordedDate' column must be in a timezone-aware 
    datetime format (UTC). The function will automatically convert `start_date` 
    and `end_date` to UTC if they are timezone-naive.

    Parameters:
    ----------
    responses_df : pd.DataFrame
        The DataFrame containing survey responses with a 'recordedDate' column 
        in ISO format.
    start_date : str or datetime-like
        The start of the date range, inclusive. It should be in a format 
        compatible with `pd.to_datetime`.
    end_date : str or datetime-like
        The end of the date range, inclusive. It should be in a format 
        compatible with `pd.to_datetime`.

    Returns:
    -------
    pd.DataFrame
        A subset of `responses_df` where the 'recordedDate' is within the 
        specified date range.
        
    Example:
    -------
    >>> responses_df = subset_by_date_range(responses_df, '2024-06-27', '2024-07-08')
    """

    # Ensure the 'recordedDate' column is in datetime format and set to UTC if needed
    responses_df['recordedDate'] = pd.to_datetime(responses_df['recordedDate']).dt.tz_convert('UTC')

    # Convert the start and end dates to datetime with UTC timezone
    start_date = pd.to_datetime(start_date).tz_localize('UTC')
    end_date = pd.to_datetime(end_date).tz_localize('UTC')
    
    # Subset the DataFrame based on the date range
    subset_df = responses_df[(responses_df['recordedDate'] >= start_date) & (responses_df['recordedDate'] <= end_date)]
    
    return subset_df

def list_directories(base_url, token):
    """
    List all XM Directories available to the authenticated user.

    Args:
        base_url (str): Qualtrics base URL (e.g., https://{data_center}.qualtrics.com).
        token (str): OAuth2 bearer token.

    Returns:
        dict: JSON response containing a list of directories and their IDs.
    """
    endpoint_url = f"{base_url}/API/v3/directories"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(endpoint_url, headers=headers)
    return response.json()

