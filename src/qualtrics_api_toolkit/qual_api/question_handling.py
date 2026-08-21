# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 11:07:04 2026

@author: kieranmartin
"""
import pandas as pd
import numpy as np
import re

###############################################
# get_response_export_file 
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
    # do not include FIRST_CLICK, LAST_CLICK, CLICK_COUNT or PAGE_SUBMIT from Timer feature:
    question_columns = [
        col for col in column_names
        if col.startswith('QID')
      #  and not col.endswith(('CLICK', 'SUBMIT', 'COUNT'))
    ]
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
##########################################################################
# get_survey_questions
def extract_block_details(block_id, blocks):
    """
    Extract details for a single block given its ID.
    Returns a list of dictionaries containing block name and question IDs.
    """
    block_details = blocks.get(block_id, {})
    block_name = block_details.get('description', 'No Description')
    elements = block_details.get('elements', [])
    question_ids = [element['questionId'] for element in elements if element['type'] == 'Question']

    return [{'Block Name': block_name, 'Question ID': question_id} for question_id in question_ids]


def process_survey_flow(flow_items, blocks):
    """
    Process the flow structure of the survey, handling both blocks and branches.
    Returns a list of dictionaries with block name and question IDs in the order 
    they appear.
    """
    ordered_blocks = []
    for flow_item in flow_items:
        if flow_item.get('type') == 'Block':  # Standard block
            block_id = flow_item.get('id')
            ordered_blocks.extend(extract_block_details(block_id, blocks))
        elif flow_item.get('type') == 'Branch':  # Nested branch
            nested_flow = flow_item.get('flow', [])
            # Recursively process nested flow:
            ordered_blocks.extend(process_survey_flow(nested_flow, blocks)) 
    return ordered_blocks


def get_block_data(survey_questions):
    """
    Fetches survey data from the Qualtrics API, extracts block names and their 
    associated questions, and returns a DataFrame with the ordered blocks and 
    question IDs.

    Args:
        base_url (str): The base URL for the Qualtrics API.
        survey_id (str): The unique ID of the survey to fetch.
        token (str): The API token for authentication.

    Returns:
        blocks_df (pd.DataFrame): A DataFrame with Block Name and Question ID 
                                 columns.
    """
    blocks = survey_questions.get('blocks', {})
    flow = survey_questions.get('flow', [])
    ordered_blocks = process_survey_flow(flow, blocks)
    blocks_df = pd.DataFrame(ordered_blocks)
    return blocks_df


###############################################################################
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


def handle_matrix_question(
        current_question, 
        split_column_name,          
        question_text_list, 
        long_text_id_list, 
        question_value_list, 
        answer_id_list, 
        keep_question_list
):
    """
    Handles extraction for Matrix question types.

    This function processes Matrix-type questions by appending their main question text
    and sub-question text to the question_text_list. For each sub-question, it captures
    the unique sub-question ID and iterates through the answer choices to extract 
    relevant details such as answer IDs and values. If an image description is available 
    for a choice, it is used as the answer value; otherwise, choiceText is used.

    Parameters:
    - current_question (dict): The current question dictionary from the survey.
    - split_column_name (list): A split representation of the column name to identify sub-questions.
    - question_text_list (list): List to append the combined question and sub-question text.
    - long_text_id_list (list): List to append unique sub-question IDs.
    - question_value_list (list): List to append answer values (imageDescription or choiceText).
    - answer_id_list (list): List to append answer IDs (recode values).
    - keep_question_list (list): List to append a boolean indicating if the question should be kept.

    Returns:
    None
    """
    main_question_text = current_question.get('questionText')
    sub_question_text = current_question.get('subQuestions').get(split_column_name[1]).get('choiceText')
    question_text_list.append(f"{main_question_text}| {sub_question_text}")
    keep_question_list.append(True)
    
    # Ensure each sub-question ID (e.g., QID11_1) is correctly captured
    sub_question_id = split_column_name[0] + "_" + split_column_name[1]
    
    # Append answer choices for each sub-question with unique sub-question IDs
    choices = current_question.get('choices')
    for choice_key, choice in choices.items():
        long_text_id_list.append(sub_question_id)  # Use sub-question ID here
        answer_id_list.append(choice.get('recode'))
        # Use imageDescription if available, otherwise fallback to choiceText
        question_value_list.append(
            choice.get('imageDescription') or choice.get('choiceText')
        )


def handle_cs_question(
        current_question, 
        split_column_name, 
        question_text_list, 
        is_numeric_list, 
        keep_question_list
):
    """
    Handles extraction for Cumulative Sum (CS) question types.
    """
    main_question_text = current_question.get('questionText')
    choices = current_question.get('choices')
    sub_question_text = choices.get(split_column_name[1]).get('choiceText')
    question_text_list.append(f"{main_question_text}| {sub_question_text}")
    is_numeric_list[-1] = True
    keep_question_list.append(True)


def handle_ro_question(
        current_question, 
        split_column_name, 
        question_text_list, 
        long_text_id_list, 
        question_value_list, 
        answer_id_list, 
        keep_question_list, 
        base_url, 
        token, 
        survey_id
):
    """
    Handles extraction for Rank Order (RO) question types, ensuring rank items 
    are correctly added to question_values_df.
    """
    if split_column_name[-1] == 'TEXT':
        question_text_list.append(current_question.get('questionText'))
        keep_question_list.append(True)
    else:
        survey_info = get_full_survey_info(base_url, token, survey_id)
        question_id_prefix = split_column_name[0]  # Example: "QID10"
        
        # Retrieve choice order for the main question
        choice_order = survey_info['result']['Questions'][question_id_prefix].get('ChoiceOrder')
        
        # Get the rank position for this column (e.g., "1" in "QID10_1")
        rank_position = int(split_column_name[1]) - 1  # Adjust to zero-based indexing
        current_key = str(choice_order[rank_position])

        main_question_text = current_question.get('questionText')
        choices = current_question.get('choices')
        
        # Retrieve sub-question text for this rank option
        sub_question_text = choices.get(current_key).get('imageDescription') or choices.get(current_key).get('choiceText')
        question_text_list.append(f"{main_question_text} | {sub_question_text}")
        keep_question_list.append(True)

        # Append numeric ranks for each choice in the rank order question
        rank_question_id = f"{question_id_prefix}_{rank_position + 1}"
        for rank, choice_key in enumerate(choice_order, start=1):
            long_text_id_list.append(rank_question_id)  # Use unique rank item ID here
            answer_id_list.append(rank)
            question_value_list.append(str(rank))  # Rank values as strings (1, 2, 3, etc.)


def handle_slider_question(
        current_question, 
        split_column_name, 
        question_text_list, 
        is_numeric_list, 
        keep_question_list, 
        long_text_id_list, 
        question_value_list, 
        answer_id_list
):
    """
    Handles extraction for Slider question types, ensuring each possible value 
    on the slider is added to question_values_df, with the full question_id 
    including any suffix to distinguish sub-questions.
    
    IMPORTANT: qualtrics API doesnt return the number of stars available 
    when pulling 'Choices' instead 'Choices' is how many slider sub-questions 
    there are. Therefore, the slider_range below will need to be adjusted based 
    on how many stars were available in the survey. Suggest that we keep to max 
    5 to avoid issues with this.
    """
    main_question_text = current_question.get('questionText')
    choices = current_question.get('choices')
    
    if split_column_name[-1] == 'TEXT':
        question_text_list.append(main_question_text)
        keep_question_list.append(True)
    else:
        # Assuming sliders range from 1 to 5; adjust if range differs
        slider_range = range(1, 6)  # Replace with actual slider range if known
        full_question_id = f"{split_column_name[0]}_{split_column_name[1]}"  # e.g., "QID12_1"
        
        for value in slider_range:
            long_text_id_list.append(full_question_id)
            answer_id_list.append(value)
            question_value_list.append(str(value))  
        
        sub_question_text = choices.get(split_column_name[1], {}).get('choiceText', '')
        question_text_list.append(f"{main_question_text} | {sub_question_text}")
        keep_question_list.append(True)


def handle_timing_question(
        current_question, 
        question_text_list, 
        is_numeric_list, 
        keep_question_list
):
    """
    Handles extraction for Timing question types.
    """
    question_text_list.append(current_question.get('questionText'))
    is_numeric_list[-1] = True
    keep_question_list.append(True)


def handle_graphic_slider(
        current_question, 
        question_selector_list, 
        question_text_list, 
        is_numeric_list, 
        keep_question_list
):
    """
    Handles extraction for Graphic Slider (SS) question types.
    """
    if question_selector_list == 'TA':
        question_text_list.append(current_question.get('questionText'))
        is_numeric_list[-1] = True
        keep_question_list.append(True)
    else:
        print('Problems with Type SS (Graphical Slider)!!')


def handle_pgr_question(
        current_question, 
        split_column_name, 
        question_text_list, 
        group_question_id_list, 
        group_answer_id_list, 
        group_value_list, 
        keep_question_list
):
    """
    Handles extraction for PGR (Pick, Group, Rank) question types.
    """
    if split_column_name[-1] == 'GROUP':
        main_question_text = current_question.get('questionText')
        groups = current_question.get('groups')
        sub_question_text = groups.get(split_column_name[1]).get('description')
        question_text_list.append(f"{main_question_text}| {sub_question_text}")
        keep_question_list.append(True)
        items = current_question.get('items')
        for item_key in items:
            current_item = items.get(item_key)
            group_question_id_list.append(split_column_name[0])
            group_answer_id_list.append(item_key)
            group_value_list.append(current_item.get('description'))


def handle_default_question(
        current_question, 
        split_column_name, 
        question_text_list, 
        long_text_id_list, 
        question_value_list, 
        answer_id_list, 
        question_type_list, 
        question_selector_list, 
        keep_question_list
):
    """
    Handles the default case for question types not specifically handled.
    """
    question_text_list.append(current_question.get('questionText'))
    keep_question_list.append(True)
    if current_question.get('questionType').get('type') == 'MC':
        if split_column_name[-1] == 'TEXT':
            question_type_list[-1] = 'TE'
            question_selector_list[-1] = 'TE'
        else:
            choices = current_question.get('choices')
            for choice_key in choices:
                current_choice = choices.get(choice_key)
                long_text_id_list.append(split_column_name[0])
                answer_id_list.append(current_choice.get('recode'))
                # Use imageDescription if available, otherwise fallback to choiceText
                question_value_list.append(
                    current_choice.get('imageDescription') or current_choice.get('choiceText')
                )


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
    }).astype(str)
    
    return question_df, question_values_df


def extract_column_data_types(question_dictionary, responses_df, base_url, token, survey_id):
    """
    Extracts column data types and question details from a survey.
    
    Parameters:
    - question_dictionary (dict): Survey dictionary with questions.
    - responses_df (pd.DataFrame): Survey response DataFrame.
    - base_url (str): Base URL for Qualtrics API.
    - token (str): API token.
    - survey_id (str): Survey ID.
    
    Returns:
    - question_df (pd.DataFrame): DataFrame containing question details.
    - question_values_df (pd.DataFrame): DataFrame containing question values 
                                         and answer IDs.
    """
    # Extract column names from responses DataFrame
    column_names = responses_df.columns
    question_columns = [col for col in column_names if 'QID' in col]
    
    if len(question_columns) == 0:
        return pd.DataFrame(), pd.DataFrame()
    
    # Initialize lists for different question properties
    question_id_list = []
    question_name_list = []
    question_text_list = []
    question_type_list = []
    question_selector_list = []
    
    # Initialize lists for question details
    long_text_id_list = []
    question_value_list = []
    answer_id_list = []
    is_numeric_list = []
    keep_question_list = []
    
    # Initialize lists for group-related data
    group_question_id_list = []
    group_value_list = []
    group_answer_id_list = []
    
    # List of survey question keys
    key_list = list(question_dictionary.keys())

    for col in question_columns:
        split_column_name = re.split('_|#', col)  # Split on underscores or # for QID
        qid_index = [i for i in range(len(split_column_name)) if 'QID' in split_column_name[i]]

        if split_column_name[qid_index[0]] in key_list:
            current_question = question_dictionary.get(split_column_name[qid_index[0]])
            
            # Append basic question properties
            question_id_list.append(col)
            question_name_list.append(current_question.get('questionName'))
            current_type = current_question.get('questionType').get('type')
            question_type_list.append(current_type)
            question_selector_list.append(current_question.get('questionType').get('selector'))

            # Check if question type is numeric
            is_numeric_list.append(is_numeric(current_question))
            
            # Handle different question types
            if current_type == 'Matrix':
                handle_matrix_question(
                    current_question, 
                    split_column_name, 
                    question_text_list, 
                    long_text_id_list, 
                    question_value_list, 
                    answer_id_list, 
                    keep_question_list
                )
            elif current_type == 'CS':
                handle_cs_question(
                    current_question, 
                    split_column_name, 
                    question_text_list, 
                    is_numeric_list, 
                    keep_question_list
                )
            elif current_type == 'RO':
                handle_ro_question(
                    current_question, 
                    split_column_name, 
                    question_text_list, 
                    long_text_id_list, 
                    question_value_list, 
                    answer_id_list, 
                    keep_question_list, 
                    base_url, 
                    token, 
                    survey_id
                )
            elif current_type == 'Slider':
                handle_slider_question(
                    current_question, 
                    split_column_name, 
                    question_text_list, 
                    is_numeric_list, 
                    keep_question_list, 
                    long_text_id_list, 
                    question_value_list, 
                    answer_id_list
                )
            elif current_type == 'Timing':
                handle_timing_question(
                    current_question, 
                    question_text_list, 
                    is_numeric_list, 
                    keep_question_list
                )
            elif current_type == 'SS':
                handle_graphic_slider(
                    current_question, 
                    question_selector_list, 
                    question_text_list, 
                    is_numeric_list, 
                    keep_question_list
                )
            elif current_type == 'PGR':
                handle_pgr_question(
                    current_question, 
                    split_column_name, 
                    question_text_list, 
                    group_question_id_list, 
                    group_answer_id_list, 
                    group_value_list, 
                    keep_question_list
                )
            else:
                handle_default_question(
                    current_question, 
                    split_column_name, 
                    question_text_list, 
                    long_text_id_list, 
                    question_value_list, 
                    answer_id_list, 
                    question_type_list, 
                    question_selector_list, 
                    keep_question_list
                )
    
    # Convert lists to numpy arrays and create DataFrames
    question_df, question_values_df = create_question_dataframes(
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
    )
    
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
        & np.array(question_df['is_numeric'] == False)
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


def reorder_question_df_with_normalized_ids(question_df, blocks_df, drop_na=False):
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
    reordered_question_df = merged_df.drop(
        columns=['normalized_id']
        ).reset_index(drop=True)

    if drop_na:
        reordered_question_df = (
            reordered_question_df
            .dropna()
            .reset_index(drop=True)
        )
        
    return reordered_question_df


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