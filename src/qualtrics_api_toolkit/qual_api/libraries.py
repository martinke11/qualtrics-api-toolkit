# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 11:07:04 2026

@author: kieranmartin
"""
import requests

# Library Blocks:
def list_library_blocks():
    return


# Libraries:
def list_libraries(base_url, token):
    """
    Fetch all libraries available to the caller in Qualtrics.

    Parameters:
        base_url (str): The base URL for the Qualtrics API.
        token (str): Bearer token for authorization.

    Returns:
        dict: Parsed JSON response from the Qualtrics API containing the 
        list of libraries.

    Raises:
        Exception: If the API request fails.
    """
    endpoint_url = f"{base_url}/API/v3/libraries"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(endpoint_url, headers=headers)
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching libraries: {e}")


# Library Questions
def list_library_questions():
    return


# Library Surveys:
def list_library_surveys():
    return


# Library Messages:
def list_library_messages(base_url, token, library_id, category=None, offset=0):
    """
    Fetch all messages from a specified library in Qualtrics.

    Parameters:
        base_url (str): The base URL for the Qualtrics API.
        token (str): Bearer token for authorization.
        library_id (str): The ID of the library to fetch messages from.
        category (str, optional): The category a message belongs to (e.g., invite, thankYou).
        offset (int, optional): The starting position for pagination. Default is 0.

    Returns:
        dict: Parsed JSON response from the Qualtrics API containing the list 
             of messages.

    Raises:
        Exception: If the API request fails.
    """
    endpoint_url = f"{base_url}/API/v3/libraries/{library_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    params = {
        "category": category,
        "offset": offset
    }

    # Remove None values from params to avoid sending unnecessary keys
    params = {key: value for key, value in params.items() if value is not None}

    try:
        response = requests.get(endpoint_url, headers=headers, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching library messages: {e}")


def create_library_message(
    base_url, 
    token, 
    library_id, 
    description, 
    category, 
    messages
):
    """
    Creates a new message in a specified Qualtrics library.

    Args:
        base_url (str): The base URL of your Qualtrics data center, 
                        e.g., 'https://{data_center}.qualtrics.com'.
        token (str): OAuth2 bearer token with the 'write:libraries' scope.
        library_id (str): The Qualtrics Library ID (e.g., 'UR_12345abcdef').
        description (str): Description for the new message.
        category (str): The category for the new message. Possible values include:
                        'invite', 'thankYou', 'reminder', 'endOfSurvey', 
                        'inactiveSurvey', 'general', 'lookAndFeel', 'emailSubject',
                        'smsInvite', 'smsReminder', 'smsThankYou', 'validation',
                        'evaluatorInvite', 'evaluatorReminder', 'subjectLine'.
        messages (dict): A dictionary of language-code keys and message text values.
                         Example: {"en": "Example English message.", "pt-br": "Mensagem em Português."}

    Returns:
        dict: JSON response from the Qualtrics API. 
    """
    endpoint_url = f"{base_url}/API/v3/libraries/{library_id}/messages"

    payload = {
        "description": description,
        "category": category,
        "messages": messages
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
        
    }

    response = requests.post(endpoint_url, headers=headers, json=payload)
    return response.json()


def get_library_message(base_url, token, library_id, message_id):
    """
    Retrieves a specific message from a Qualtrics library.

    Args:
        base_url (str): The base URL of your Qualtrics data center,
                        e.g., 'https://{data_center}.qualtrics.com'.
        token (str): OAuth2 bearer token with the 'read:libraries' scope.
        library_id (str): The Qualtrics Library ID (e.g., 'UR_12345abcdef').
        message_id (str): The Qualtrics Message ID (e.g., 'MS_67890abcxyz').

    Returns:
        dict: JSON response from the Qualtrics API. 
    """
    endpoint_url = (
        f"{base_url}/API/v3/libraries/{library_id}"
        f"/messages/{message_id}"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(endpoint_url, headers=headers)
    response.raise_for_status()  # (Optional) Raise HTTPError for bad responses
    return response.json()


def update_library_message(
        base_url, 
        token, 
        library_id, 
        description, 
        category, 
        messages, 
        message_id
):
    """
    Updates a library message
    """
    endpoint_url = (
        f"{base_url}/API/v3/libraries/{library_id}"
        f"/messages/{message_id}"
    )
    payload = {
        "description": description,
        "messages": messages
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.put(endpoint_url, headers=headers, json=payload)
    return response.json()


def delete_library_message(
        base_url, 
        token, 
        library_id, 
        category, 
        message_id
):
    """
    Deletes a message from a library
    """
    endpoint_url = (
        f"{base_url}/API/v3/libraries/{library_id}"
        f"/messages/{message_id}"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.delete(endpoint_url, headers=headers)
    return response.json()


# Library Graphics:
def upload_graphic():
    return

def delete_graphic():
    return
