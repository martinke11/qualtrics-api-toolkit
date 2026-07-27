import requests
import pandas as pd

from src.qual_api.utils import strip_html

def get_survey_list(base_url, token):
    """
    Retrieve a complete list of surveys from the Qualtrics API, handling pagination if necessary.
    
    This function makes repeated API requests to the Qualtrics survey endpoint to retrieve all surveys.
    It handles the pagination of results by checking for a "nextPage" key in the API response, which 
    provides an offset for subsequent pages of data. The function returns the complete survey list in 
    the form of a Pandas DataFrame.
    
    Args:
        base_url (str): The base URL for the Qualtrics API.
        token (str): The API token used for authorization.

    Returns:
        pd.DataFrame: A DataFrame containing the complete list of surveys with their details.
        
    Raises:
        requests.exceptions.RequestException: If there's an error with the API request.
    """
    # Initialize the flag to track pagination and the offset for next pages
    flag = True
    count = 0
    offset = ""
    
    while flag:
        # Determine the URL based on whether it's the first page or a subsequent page
        if count == 0:
            url = '{0}/API/v3/surveys'.format(base_url)
        else:
            url = '{0}/API/v3/surveys?offset={1}'.format(base_url, offset)
        
        # Make the API request
        response = requests.get(url, headers={"Authorization": "Bearer " + token})
        response_json = response.json()

        # Extract the current page of survey results into a DataFrame
        current_page_df = pd.DataFrame(response_json.get("result").get("elements"))
        
        # For the first page, initialize the DataFrame; for others, append to it
        if count == 0:
            survey_list_df = current_page_df
        else:
            survey_list_df = pd.concat([survey_list_df, current_page_df])
            
        # Check if there's a next page and update flag and offset accordingly
        if response_json.get("result").get("nextPage") is None:
            flag = False
        else:
            next_page_str = response_json.get("result").get("nextPage")
            offset = next_page_str.split("?offset=", 1)[1]
            count += 1
    
    # Reset the indices of the final DataFrame and return it
    survey_list_df = survey_list_df.reset_index(drop=True)
    
    return survey_list_df


def get_survey_id_by_name(survey_list_df, survey_name):
    """
    Retrieves the survey ID based on the survey name from a DataFrame.

    Args:
        survey_list_df (pd.DataFrame): A DataFrame containing survey data with 'name' and 'id' columns.
        survey_name (str): The name of the survey to search for.

    Returns:
        str: The survey ID if found, or None if not found or multiple surveys have the same name.
    """
    # Pull the indices associated with the Survey Name
    survey_name_indices = survey_list_df.loc[survey_list_df['name'] == survey_name].index[:]
    
    if len(survey_name_indices) > 1:
        print('Multiple Surveys Have the Same Name!!!')
        return None  # Return None to indicate multiple surveys found
    elif len(survey_name_indices) == 0:
        print('Cannot Find the Survey. Please Check that the Survey Name is Correct.')
        return None  # Return None to indicate survey not found
    else:
        # Return the survey ID using the survey index
        survey_id = survey_list_df.loc[survey_name_indices[0], 'id']
        return survey_id


def get_full_survey_info(base_url, token, survey_id):
    """
    Retrieves full survey information, pulling more detailed info.

    Args:
        base_url (str): Base URL for the API.
        access_token (str): Access token for authentication.
        survey_id (str): Survey ID.

    Returns:
        dict: Full survey information.
    """
    full_survey_info_url = '{0}/API/v3/survey-definitions/{1}'.format(base_url, survey_id)
    response = requests.get(full_survey_info_url,
                            headers={"Content-Type": "application/json",
                                     "Authorization": "Bearer " + token})
    return response.json()

def get_survey_meta(base_url, token, survey_id):
    """
    Fetches the metadata for a given survey from the API.

    Args:
        base_url (str): The base URL for the API.
        token (str): The authorization token for the API.
        survey_id (str): The ID of the survey to fetch metadata for.

    Returns:
        dict: A JSON object containing the survey's metadata.
    """
    endpoint_url = '{0}/API/v3/survey-definitions/{1}/metadata'.format(base_url, survey_id)
    
    # Pull the survey metadata
    response = requests.get(endpoint_url, 
                            headers={"Content-Type": "application/json",
                                     "Authorization": "Bearer " + token}) 

    # Convert the data into a more readable format
    response = response.json()    
    return response

def get_survey_questions(base_url, token, survey_id):
    """
    Retrieve the questions from a specific survey in the Qualtrics API and 
    clean the data by stripping HTML tags.

    This function fetches the survey questions from a specified survey using 
    the Qualtrics API. It returns the survey data as a dictionary and removes 
    any HTML tags that may be present in the survey question text.

    Args:
        base_url (str): The base URL for the Qualtrics API.
    token (str): The API token used for authorization.
        survey_id (str): The unique ID of the survey whose questions are 
        being retrieved.

    Returns:
        dict: A dictionary containing the survey questions with HTML tags removed.
        
    Raises:
        requests.exceptions.RequestException: If there's an error with the API request.
    """
    # Set the URL for the specific survey
    survey_url = '{0}/API/v3/surveys/{1}'.format(base_url, survey_id)
    
    response = requests.get(survey_url, headers={"Authorization": "Bearer " + token})
    
    # Convert the data into a more readable format
    survey_question_dictionary = response.json()

    # Apply HTML cleaning on the survey questions inside 'result'
    if (
        'result' in survey_question_dictionary
        and 'questions' in survey_question_dictionary['result']
    ):
        for question_id, question_data in (
            survey_question_dictionary['result']['questions'].items()
        ):
            if 'questionText' in question_data:
                question_data['questionText'] = (
                    strip_html(question_data['questionText']).strip()
                )
            if 'choices' in question_data:
                question_data['choices'] = strip_html(question_data['choices'])
            
    return survey_question_dictionary

def get_block_data(base_url, survey_id, token):
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
    survey_url = f'{base_url}/API/v3/surveys/{survey_id}'
    response = requests.get(survey_url, headers={"Authorization": f"Bearer {token}"})
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch survey data: {response.status_code}, {response.text}")
    
    survey_question_dictionary = response.json()

    survey_result = survey_question_dictionary.get('result', {})
    blocks = survey_result.get('blocks', {})
    flow = survey_result.get('flow', [])

    # Process the survey flow to get ordered blocks
    ordered_blocks = process_survey_flow(flow, blocks)

    blocks_df = pd.DataFrame(ordered_blocks)

    return blocks_df


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
    Returns a list of dictionaries with block name and question IDs in the order they appear.
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


def change_survey_metadata(base_url, token, survey_id, metadata):
    """
    Updates a survey's metadata.

    Args:
        base_url (str): Base URL for the API.
        access_token (str): Access token for authentication.
        survey_id (str): Survey ID.
        metadata (dict): Metadata to update.

    Returns:
        dict: Response from the API.
    """
    survey_metadata_url = '{0}/API/v3/survey-definitions/{1}/metadata'.format(base_url, survey_id)
    response = requests.put(survey_metadata_url,
                            headers={"Content-Type": "application/json",
                                     "Authorization": "Bearer " + token},
                            data=metadata)
    return response.json()


def update_survey(base_url, token, survey_id, data):
    """
    Updates a survey's details.

    Args:
        base_url (str): Base URL for the API.
        access_token (str): Access token for authentication.
        survey_id (str): Survey ID.
        data (dict): Data to update.

    Returns:
        dict: Response from the API.
    """
    survey_update_url = '{0}/API/v3/surveys/{1}'.format(base_url, survey_id)
    response = requests.put(survey_update_url,
                            headers={"Content-Type": "application/json",
                                     "Authorization": "Bearer " + token},
                            data=data)
    return response.json()



def share_survey(base_url, token, survey_id, recipient_id, permissions):
    """
    Shares a survey with another user in your brand.

    Args:
        base_url (str): Qualtrics base URL (e.g., https://{data_center}.qualtrics.com).
        token (str): Your Qualtrics API token.
        survey_id (str): The unique identifier for the survey (e.g., SV_...).
        recipient_id (str): The userId or groupId the survey is shared with.
        permissions (dict): The permissions object specifying the various permissions being assigned.

    Returns:
        dict: JSON response from the API.
    """
    endpoint_url = f"{base_url}/surveys/{survey_id}/permissions/collaborations"
    data = {
        "recipientId": recipient_id,
        "permissions": permissions
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-TOKEN": token
    }
    
    response = requests.post(endpoint_url, headers=headers, json=data)
    return response.json()