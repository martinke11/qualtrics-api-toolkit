# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 11:07:04 2026

@author: kieranmartin
"""
import requests

# Users:
def get_list_users(base_url, token):
    """
    Fetches the list of users from the API.

    Args:
        base_url (str): The base URL for the API.
        token (str): The authorization token for the API.

    Returns:
        dict: A JSON object containing the list of users.
    """
    endpoint_url = f'{base_url}/API/v3/users'
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    response = requests.get(
        endpoint_url, 
        headers=headers
    ) 
    
    # Convert the data into a more readable format
    response = response.json()    
    return response


def create_user():
    return


def get_user():
    return


def delete_user():
    return


def update_user():
    return


# "Who Am I" Endpoint
def get_user_identity(base_url, token):
    """
    Retrieves the identity of the current user.

    Args:
        base_url (str): Base URL for the API.
        access_token (str): Access token for authentication.

    Returns:
        dict: User identity information.
    """
    endpoint_url = f'{base_url}/API/v3/whoami'
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    response = requests.get(
        endpoint_url,
        headers=headers
    )
    return response.json()


# Users API Tokens
def get_user_api_token():
    return

def update_user_api_token():
    return

def create_userUapi_token():
    return
