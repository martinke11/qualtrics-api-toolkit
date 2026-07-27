import os
import json
import requests

def load_config(config_filename="config.json") -> dict:
    """
    Load and return the JSON config from ~/config.json
    """
    home_directory = os.path.expanduser("~")
    config_file_path = os.path.join(home_directory, config_filename)
    with open(config_file_path, "r") as f:
        return json.load(f)

def set_project_directory(config_filename="config.json") -> str:
    """
    Change into your Qualtrics‑API repo root (from config["qualtrics_api"]["root"])
    and return that path.
    """
    config = load_config(config_filename)
    PROJECT_DIRECTORY = os.path.expanduser(config["qualtrics_api"]["qualtrics_api_root"])
    os.chdir(PROJECT_DIRECTORY)
    return PROJECT_DIRECTORY

def get_sql_credentials_path(config_filename="config.json") -> str:
    """
    Expand and return the path to your SQL creds file
    as defined in your config.json.
    """
    config = load_config(config_filename)
    return os.path.expanduser(config["sql_credentials_path"])


def read_credentials(file_path):
    """
    Reads credentials from txt file in order for this python script to access the 
    data warehouse and execute the query

    Args:
        file_path(str): Path to credentials file on local
    Returns:
        dictionary(dict): the credentials file as a dictionary pulled into 
        python environment
    """
    creds = {}
    with open(file_path, 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            key, value = line.split('=', 1)
            creds[key.strip()] = value.strip()
    return creds

def get_qualtrics_credentials_path(config_filename="config.json") -> str:
    """
    Return the expanded path to your Qualtrics creds JSON
    as defined in your config.json.
    """
    config = load_config(config_filename)
    return os.path.expanduser(config["qualtrics_api"]["qualtrics_credentials_path"])

def get_token(base_url, client_id, client_secret, data):
    """
   Requests an OAuth2 token that will last for one hour.

   Args:
       base_url (str): The base URL for the API.
       client_id (str): The client ID for authentication.
       client_secret (str): The client secret for authentication.
       data (dict): A dictionary containing data for the token request, including
                    grant type and other relevant parameters.

   Returns:
       dict: A JSON object containing the token and related information.

   Available scopes:
        - manage:activity_logs
        - manage:all
        - manage:contact_frequency_rules
        - manage:contact_transactions
        - manage:customer_data_requests
        - manage:directories
        - manage:directory_contacts
        - manage:distributions
        - manage:divisions
        - manage:erasure_requests
        - manage:groups
        - manage:libraries
        - manage:mailing_list_contacts
        - manage:mailing_lists
        - manage:organizations
        - manage:participants
        - manage:samples
        - manage:subscriptions
        - manage:survey_responses
        - manage:survey_sessions
        - manage:surveys
        - read:activity_logs
        - read:contact_frequency_rules
        - read:contact_transactions
        - read:directories
        - read:directory_contacts
        - read:distributions
        - read:divisions
        - read:groups
        - read:imported_data_projects
        - read:libraries
        - read:mailing_list_contacts
        - read:mailing_lists
        - read:organizations
        - read:participants
        - read:samples
        - read:subscriptions
        - read:survey_responses
        - read:survey_sessions
        - read:surveys
        - read:users
        - write:automations
        - write:contact_frequency_rules
        - write:contact_transactions
        - write:directory_contacts
        - write:distributions
        - write:divisions
        - write:embedded_dashboards
        - write:embedded_xid_profile_cards
        - write:groups
        - write:imported_data_projects
        - write:libraries
        - write:mailing_list_contacts
        - write:mailing_lists
        - write:participants
        - write:samples
        - write:subscriptions
        - write:survey_responses
        - write:survey_sessions
        - write:surveys
        - manage:all
        - manage:contact_frequency_rules
        - manage:activity_logs
        - manage:contact_transactions
        - manage:customer_data_requests
        - manage:directories
        - manage:directory_contacts
        - manage:distributions
        - manage:divisions
        - manage:erasure_requests
        - manage:groups
        - manage:libraries
        - manage:mailing_list_contacts
        - manage:mailing_lists
        - manage:organizations
        - manage:participants
        - manage:samples
        - manage:subscriptions
        - manage:survey_responses
        - manage:survey_sessions
        - manage:surveys
        - read:activity_logs
        - read:contact_frequency_rules
        - read:contact_transactions
        - read:directories
        - read:directory_contacts
        - read:distributions
        - read:divisions
        - read:groups
        - read:imported_data_projects
        - read:libraries
        - read:mailing_list_contacts
        - read:mailing_lists
        - read:organizations
        - read:participants
        - read:samples
        - read:subscriptions
        - read:survey_responses
        - read:survey_sessions
        - read:users
        - read:surveys
        - write:automations
        - write:contact_frequency_rules
        - write:contact_transactions
        - write:directory_contacts
        - write:distributions
        - write:divisions
        - write:embedded_dashboards
        - write:embedded_xid_profile_cards
        - write:groups
        - write:imported_data_projects
        - write:libraries
        - write:mailing_list_contacts
        - write:mailing_lists
        - write:participants
        - write:samples
        - write:subscriptions
        - write:survey_responses
        - write:survey_sessions
        - write:surveys
        - write:users
        - manage:subscriptions
        - manage:survey_responses
        - manage:survey_sessions
        - manage:surveys
        - read:subscriptions
        - read:survey_responses
        - read:survey_sessions
        - read:surveys
        - write:subscriptions
        - write:survey_responses
        - write:survey_sessions
        - write:surveys
   """

    token_url = base_url + "/oauth2/token"
    
    response = requests.post(token_url, auth=(client_id, client_secret), data=data)
    
    bearer_token_response = response.json()
    token = bearer_token_response.get('access_token')
    return token