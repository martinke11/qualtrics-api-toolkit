import pandas as pd
import re

from .utils import is_numeric, create_question_dataframes
from .survey import get_full_survey_info

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
