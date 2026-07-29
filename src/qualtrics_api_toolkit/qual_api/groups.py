# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 10:27:16 2026

@author: 484843
"""
import requests

# Groups
def get_groups(base_url, token):
    """
    List Groups. Retrieves all groups.

    Args:
        base_url (str): Base URL for the API.
        access_token (str): Access token for authentication.

    Returns:
        dict: Group information.
    """
    endpoint_url = f"{base_url}/API/v3/groups"
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.get(endpoint_url, headers=headers)
    return response.json()


def create_group(
    base_url,
    token,
    name,
    group_type_id,
    division_id=None,
):
    """
    Create a new Qualtrics group.

    Administrator access is required to use this endpoint.

    Args:
        base_url (str): Qualtrics base URL.
        token (str): OAuth2 bearer token with permission to manage groups.
        name (str): Name of the new group.
        group_type_id (str): Group type ID beginning with ``GT_``.
        division_id (str, optional): Division ID beginning with ``DV_``.

    Returns:
        dict: JSON response containing the newly created group ID.
    """
    groups_url = f"{base_url}/API/v3/groups"

    data = {
        "name": name,
        "type": group_type_id,
    }

    if division_id is not None:
        data["divisionId"] = division_id
        
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
        
    }
    response = requests.post(
        groups_url,
        headers=headers,
        json=data,
    )

    return response.json()


def get_group_details(base_url, token, group_id):
    """
    Retrieve details for a single group by ID.

    Args:
        base_url (str): The base URL of your Qualtrics data center.
        token (str): OAuth2 bearer token used to authenticate.
        group_id (str): The ID of the group (e.g., 'GR_dms1ySSxMJNZkF0').

    Returns:
        dict: A JSON response containing details of the group, including 'type'.
    """
    endpoint_url = f"{base_url}/API/v3/groups/{group_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
        
    }
    response = requests.get(endpoint_url, headers=headers)
    return response.json()


# Missing update_group


# Missing Delete Group


# Group Members
def list_users_in_group(base_url, token, group_id, offset=0):
    """
    Retrieves a list of users in a specific Qualtrics group.

    Args:
        base_url (str): The base URL of your Qualtrics data center 
        (e.g., 'https://{data_center}.qualtrics.com').
        token (str): OAuth2 bearer token with read:groups scope.
        group_id (str): The Qualtrics Group ID, e.g., 'GR_12345abcdef'.
        offset (int): Pagination offset, default is 0.

    Returns:
        dict: JSON response from the Qualtrics API, including:
              - result['elements']: List of users in the group.
              - result['nextPage']: URL for the next page of results (if applicable).
    """
    endpoint_url = f"{base_url}/API/v3/groups/{group_id}/members"
    params = {
        "offset": offset
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(endpoint_url, headers=headers, params=params)
    return response.json()


def add_user_to_group(base_url, token, group_id, user_id):
    """
    Adds a single user to a Qualtrics group.

    Args:
        base_url (str): Qualtrics base URL, e.g., https://{data_center}.qualtrics.com
        token (str): OAuth2 bearer token with write:groups scope.
        group_id (str): The Qualtrics Group ID, e.g., 'GR_9TttXzNhREpoOBE'
        user_id (str): The single user ID to add, e.g., 'UR_9HxQQrko6McPT82'

    Returns:
        dict: JSON response from Qualtrics API
    """
    endpoint_url = f"{base_url}/API/v3/groups/{group_id}/members"
    
    # The body must have just "userId" per Qualtrics docs:
    data = {
        "userId": user_id
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(endpoint_url, headers=headers, json=data)
    return response.json()


def remove_user_from_group(base_url, token, group_id, user_id):
    """
    Adds a single user to a Qualtrics group.

    Args:
        base_url (str): Qualtrics base URL, e.g., https://{data_center}.qualtrics.com
        token (str): OAuth2 bearer token with write:groups scope.
        group_id (str): The Qualtrics Group ID, e.g., 'GR_9TttXzNhREpoOBE'
        user_id (str): The single user ID to add, e.g., 'UR_9HxQQrko6McPT82'

    Returns:
        dict: JSON response from Qualtrics API
    """
    endpoint_url = f"{base_url}/API/v3/groups/{group_id}/members/{userId}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
        
    }

    response = requests.delete(endpoint_url, headers=headers)
    return response.json()
