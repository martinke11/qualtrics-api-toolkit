import requests

def get_users(base_url, token):
    """
    Fetches the list of users from the API.

    Args:
        base_url (str): The base URL for the API.
        token (str): The authorization token for the API.

    Returns:
        dict: A JSON object containing the list of users.
    """
    endpoint_url = '{0}/API/v3/users'.format(base_url)
    
    response = requests.get(endpoint_url, 
                            headers={"Content-Type": "application/json",
                                     "Authorization": "Bearer " + token}) 
    
    # Convert the data into a more readable format
    response = response.json()    
    return response


def get_user_identity(base_url, token):
    """
    Retrieves the identity of the current user.

    Args:
        base_url (str): Base URL for the API.
        access_token (str): Access token for authentication.

    Returns:
        dict: User identity information.
    """
    identity_url = '{0}/API/v3/whoami'.format(base_url)
    response = requests.get(identity_url,
                            headers={"Content-Type": "application/json",
                                     "Authorization": "Bearer " + token})
    return response.json()


def get_groups(base_url, token):
    """
    Retrieves all groups.

    Args:
        base_url (str): Base URL for the API.
        access_token (str): Access token for authentication.

    Returns:
        dict: Group information.
    """
    groups_url = '{0}/API/v3/groups'.format(base_url)
    response = requests.get(groups_url,
                            headers={"Content-Type": "application/json",
                                     "Authorization": "Bearer " + token})
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
    url = f"{base_url}/API/v3/groups/{group_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
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
        dict: JSON response from Qualtrics API, typically:
              {
                  "meta": {
                      "httpStatus": "200 - OK",
                      "requestId": "...",
                      "notice": ""
                  }
              }
    """
    endpoint_url = f"{base_url}/API/v3/groups/{group_id}/members"
    
    # The body must have just "userId" per Qualtrics docs:
    data = {
        "userId": user_id
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(endpoint_url, headers=headers, json=data)
    return response.json()


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
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(endpoint_url, headers=headers, params=params)
    return response.json()
