# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 09:20:36 2026

@author: kieranmartin
"""
import requests

# Directories
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

    response = requests.get(
        endpoint_url, 
        headers=headers
    )
    return response.json()
