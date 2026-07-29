import requests

def get_list_users(base_url, token):
    """
    Fetches the list of users from the API.

    Args:
        base_url (str): The base URL for the API.
        token (str): The authorization token for the API.

    Returns:
        dict: A JSON object containing the list of users.
    """
    endpoint_url = '{0}/API/v3/users'.format(base_url)
    
    response = requests.get(
        endpoint_url, 
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + token}
    ) 
    
    # Convert the data into a more readable format
    response = response.json()    
    return response


# Missing create_user


# Missing get_user


# Missing delete_user


# Missing update_user


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
    identity_url = '{0}/API/v3/whoami'.format(base_url)
    response = requests.get(
        identity_url,
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + token}
    )
    return response.json()
