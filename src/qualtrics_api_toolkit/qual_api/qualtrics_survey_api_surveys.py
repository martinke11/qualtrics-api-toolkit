# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 11:07:04 2026

@author: kieranmartin
"""
import requests
import pandas as pd

from src.qual_api.utils import strip_html

# Qualtrics Survey API --> Surveys
def create_survey():
    return

def get_survey(base_url, token, survey_id):
    """
    Retrieves full survey information, pulling more detailed info.

    Args:
        base_url (str): Base URL for the API.
        access_token (str): Access token for authentication.
        survey_id (str): Survey ID.

    Returns:
        dict: Full survey information.
    """
    endpoint_url = f'{base_url}/API/v3/survey-definitions/{survey_id}'
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    response = requests.get(
        endpoint_url,
        headers=headers
    )
    return response.json()


def delete_survey():
    return

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
    endpoint_url = f'{base_url}/API/v3/survey-definitions/{survey_id}/metadata'
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    response = requests.get(
        endpoint_url, 
        headers=headers
    ) 
    response = response.json()    
    return response


def update_metadata(base_url, token, survey_id, metadata):
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
    endpoint_url = f'{base_url}/API/v3/survey-definitions/{survey_id}/metadata'
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    response = requests.put(
        endpoint_url,
        headers=headers,
        data=metadata
    )
    
    return response.json()




