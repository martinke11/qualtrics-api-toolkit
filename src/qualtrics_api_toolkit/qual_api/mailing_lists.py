import requests

def list_mailing_lists(base_url, token, directory_id, page_size=100, skip_token=None, include_count=True):
    """
    Retrieves a list of mailing lists in an XM Directory.

    Args:
        base_url (str): Qualtrics base URL (e.g., https://{data_center}.qualtrics.com).
        token (str): OAuth2 bearer token with read:mailing_lists scope.
        directory_id (str): Directory ID (POOL_...).
        page_size (int): Maximum number of items to return per request (default 100).
        skip_token (str): Token for pagination (default None).
        include_count (bool): Include contact count (default False).

    Returns:
        dict: JSON response containing mailing list information.
    """
    endpoint_url = f"{base_url}/API/v3/directories/{directory_id}/mailinglists"
    params = {
        "pageSize": page_size,
        "includeCount": include_count
    }
    if skip_token:
        params["skipToken"] = skip_token

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(endpoint_url, headers=headers, params=params)
    return response.json()


def update_mailing_list_owner(base_url, token, directory_id, mailing_list_id, owner_id):
    """
    Updates the owner of a mailing list to share it with a group.

    Args:
        base_url (str): Qualtrics base URL.
        token (str): OAuth2 bearer token with `write:mailing_lists` scope.
        directory_id (str): Directory ID (POOL_...).
        mailing_list_id (str): Mailing List ID (CG_...).
        owner_id (str): Group ID to set as the owner.

    Returns:
        dict: JSON response from the API.
    """
    endpoint_url = f"{base_url}/API/v3/directories/{directory_id}/mailinglists/{mailing_list_id}"
    data = {
        "ownerId": owner_id
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.put(endpoint_url, headers=headers, json=data)
    return response.json()


def create_mailing_list(base_url, token, directory_id, name, owner_id=None, prioritize_metadata=False):
    """
    Creates a new mailing list in an XM Directory.

    Args:
        base_url (str): Qualtrics base URL (e.g., https://{data_center}.qualtrics.com).
        token (str): OAuth2 bearer token with write:mailing_lists scope.
        directory_id (str): Directory ID (POOL_...).
        name (str): Name of the mailing list.
        owner_id (str): Owner of the mailing list (default None).
        prioritize_metadata (bool): Prioritize list metadata over contact metadata (default False).

    Returns:
        dict: JSON response with the newly created mailing list's ID.
    """
    endpoint_url = f"{base_url}/API/v3/directories/{directory_id}/mailinglists"
    data = {
        "name": name,
        "prioritizeListMetadata": prioritize_metadata
    }
    if owner_id:
        data["ownerId"] = owner_id

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(endpoint_url, headers=headers, json=data)
    return response.json()



def get_mailing_list(base_url, token, directory_id, mailing_list_id, include_count=True):
    """
    Retrieves details of a specific mailing list.

    Args:
        base_url (str): Qualtrics base URL (e.g., https://{data_center}.qualtrics.com).
        token (str): OAuth2 bearer token with read:mailing_lists scope.
        directory_id (str): Directory ID (POOL_...).
        mailing_list_id (str): Mailing list ID (CG_...).
        include_count (bool): Include contact count (default False).

    Returns:
        dict: JSON response containing mailing list details.
    """
    endpoint_url = f"{base_url}/API/v3/directories/{directory_id}/mailinglists/{mailing_list_id}"
    params = {
        "includeCount": include_count
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(endpoint_url, headers=headers, params=params)
    return response.json()


def update_mailing_list(base_url, token, directory_id, mailing_list_id, name, owner_id=None):
    """
    Updates a mailing list's name or owner.

    Args:
        base_url (str): Qualtrics base URL (e.g., https://{data_center}.qualtrics.com).
        token (str): OAuth2 bearer token with write:mailing_lists scope.
        directory_id (str): Directory ID (POOL_...).
        mailing_list_id (str): Mailing list ID (CG_...).
        name (str): New name for the mailing list.
        owner_id (str): New owner of the mailing list (default None).

    Returns:
        dict: JSON response from the API.
    """
    endpoint_url = f"{base_url}/API/v3/directories/{directory_id}/mailinglists/{mailing_list_id}"
    data = {
        "name": name
    }
    if owner_id:
        data["ownerId"] = owner_id

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.put(endpoint_url, headers=headers, json=data)
    return response.json()


def delete_mailing_list(base_url, token, directory_id, mailing_list_id):
    """
    Deletes a mailing list from an XM Directory.

    Args:
        base_url (str): Qualtrics base URL (e.g., https://{data_center}.qualtrics.com).
        token (str): OAuth2 bearer token with write:mailing_lists scope.
        directory_id (str): Directory ID (POOL_...).
        mailing_list_id (str): Mailing list ID (CG_...).

    Returns:
        dict: JSON response from the API.
    """
    endpoint_url = f"{base_url}/API/v3/directories/{directory_id}/mailinglists/{mailing_list_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.delete(endpoint_url, headers=headers)
    return response.json()

