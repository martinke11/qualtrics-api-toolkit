import requests

def list_contacts_in_mailing_list(
        base_url, 
        token, 
        directory_id, 
        mailing_list_id, 
        page_size=50, 
        skip_token=None, 
        include_embedded=False
):
    """
    Retrieves a list of contacts in a specified mailing list.

    Args:
        base_url (str): Qualtrics base URL.
        token (str): OAuth2 bearer token with `read:mailing_list_contacts` scope.
        directory_id (str): Directory ID (POOL_...).
        mailing_list_id (str): Mailing List ID (CG_...).
        page_size (int): Number of contacts to retrieve per page (default: 50).
        skip_token (str): Token for pagination (default: None).
        include_embedded (bool): Include embedded data in the response.

    Returns:
        dict: JSON response containing contacts and pagination info.
    """
    endpoint_url = f"{base_url}/API/v3/directories/{directory_id}/mailinglists/{mailing_list_id}/contacts"
    params = {
        "pageSize": page_size,
        "includeEmbedded": 'true' if include_embedded else 'false'
    }
    if skip_token:
        params["skipToken"] = skip_token

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(endpoint_url, headers=headers, params=params)
    return response.json()


def create_contact_in_mailing_list(
        base_url, 
        token, 
        directory_id, 
        mailing_list_id, 
        first_name, 
        last_name, 
        email, 
        phone=None, 
        ext_ref=None, 
        embedded_data=None, 
        private_embedded_data=None, 
        language=None, 
        unsubscribed=False
):
    """
    Creates a contact in a specified mailing list.

    Args:
        base_url (str): Qualtrics base URL.
        token (str): OAuth2 bearer token with `write:mailing_list_contacts` scope.
        directory_id (str): Directory ID (POOL_...).
        mailing_list_id (str): Mailing List ID (CG_...).
        first_name (str): Contact's first name.
        last_name (str): Contact's last name.
        email (str): Contact's email.
        phone (str): Contact's phone number (optional).
        ext_ref (str): External reference for the contact (optional).
        embedded_data (dict): Additional metadata for the contact (optional).
        private_embedded_data (dict): Private metadata for the contact (optional).
        language (str): Language code for the contact (optional).
        unsubscribed (bool): Contact's subscription status (default: False).

    Returns:
        dict: JSON response containing the created contact's ID.
    """
    endpoint_url = f"{base_url}/API/v3/directories/{directory_id}/mailinglists/{mailing_list_id}/contacts"
    data = {
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
        "phone": phone,
        "extRef": ext_ref,
        "embeddedData": embedded_data,
        "privateEmbeddedData": private_embedded_data,
        "language": language,
        "unsubscribed": unsubscribed
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        endpoint_url, 
        headers=headers, 
        json={k: v for k, v in data.items() if v is not None}
    )
    return response.json()

def get_contact_lookup_id_in_mailing_list(
    base_url: str,
    token: str,
    directory_id: str,
    mailing_list_id: str,
    contact_id: str
) -> str:
    """
    Retrieve the contactLookupId (CGC_…) for a contact in a mailing list,
    using OAuth2 Bearer authentication.
    """
    url = (
        f"{base_url}/API/v3"
        f"/directories/{directory_id}"
        f"/mailinglists/{mailing_list_id}"
        f"/contacts/{contact_id}"
    )
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    resp = requests.get(url, headers=headers)
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        print("=== GET CONTACT LOOKUP FAILED ===")
        print("URL:", url)
        print("Status:", resp.status_code)
        print("Body:", resp.text)
        raise

    return resp.json()["result"]["contactLookupId"]


def list_bounced_mailing_list_contacts(
        base_url, 
        token, 
        directory_id, 
        mailing_list_id, 
        page_size=50, 
        skip_token=None, 
        since=None
):
    """
    Retrieves a list of bounced contacts in a specified mailing list.

    Args:
        base_url (str): Qualtrics base URL.
        token (str): OAuth2 bearer token with `read:mailing_list_contacts` scope.
        directory_id (str): Directory ID (POOL_...).
        mailing_list_id (str): Mailing List ID (CG_...).
        page_size (int): Number of contacts to retrieve per page (default: 50).
        skip_token (str): Token for pagination (default: None).
        since (str): Date-time string to filter bounced contacts (optional).

    Returns:
        dict: JSON response containing bounced contacts.
    """
    endpoint_url = f"{base_url}/API/v3/directories/{directory_id}/mailinglists/{mailing_list_id}/bouncedContacts"
    params = {
        "pageSize": page_size,
        "skipToken": skip_token,
        "since": since
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(
        endpoint_url, 
        headers=headers, 
        params={k: v for k, v in params.items() if v is not None}
    )
    return response.json()


def list_opted_out_mailing_list_contacts(
        base_url, 
        token, 
        directory_id, 
        mailing_list_id, 
        page_size=50, 
        skip_token=None, 
        since=None
):
    """
    Retrieves a list of opted-out contacts in a specified mailing list.

    Args:
        base_url (str): Qualtrics base URL.
        token (str): OAuth2 bearer token with `read:mailing_list_contacts` scope.
        directory_id (str): Directory ID (POOL_...).
        mailing_list_id (str): Mailing List ID (CG_...).
        page_size (int): Number of contacts to retrieve per page (default: 50).
        skip_token (str): Token for pagination (default: None).
        since (str): Date-time string to filter opted-out contacts (optional).

    Returns:
        dict: JSON response containing opted-out contacts.
    """
    endpoint_url = f"{base_url}/API/v3/directories/{directory_id}/mailinglists/{mailing_list_id}/optedOutContacts"
    params = {
        "pageSize": page_size,
        "skipToken": skip_token,
        "since": since
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(
        endpoint_url, 
        headers=headers, 
        params={k: v for k, v in params.items() if v is not None}
    )
    return response.json()


def get_mailing_list_contact(
        base_url, 
        token, 
        directory_id, 
        mailing_list_id, 
        contact_id
):
    """
    Retrieves a specific contact in a mailing list.

    Args:
        base_url (str): Qualtrics base URL.
        token (str): OAuth2 bearer token with `read:mailing_list_contacts` scope.
        directory_id (str): Directory ID (POOL_...).
        mailing_list_id (str): Mailing List ID (CG_...).
        contact_id (str): Contact ID (CID_...).

    Returns:
        dict: JSON response containing contact details.
    """
    endpoint_url = f"{base_url}/API/v3/directories/{directory_id}/mailinglists/{mailing_list_id}/contacts/{contact_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(endpoint_url, headers=headers)
    return response.json()


def update_mailing_list_contact(
    base_url, 
    token, 
    directory_id, 
    mailing_list_id, 
    contact_id, 
    **kwargs):
    """
    Updates a contact in a mailing list.

    Args:
        base_url (str): Qualtrics base URL.
        token (str): OAuth2 bearer token with `write:mailing_list_contacts` scope.
        directory_id (str): Directory ID (POOL_...).
        mailing_list_id (str): Mailing List ID (CG_...).
        contact_id (str): Contact ID (CID_...).
        kwargs: Attributes to update (e.g., firstName, lastName, email, etc.).

    Returns:
        dict: JSON response containing the update status.
    """
    endpoint_url = f"{base_url}/API/v3/directories/{directory_id}/mailinglists/{mailing_list_id}/contacts/{contact_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.put(
        endpoint_url,
        headers=headers, 
        json={k: v for k, v in kwargs.items() if v is not None})
    return response.json()


def delete_contact_from_mailing_list(base_url, token, directory_id, mailing_list_id, contact_id):
    """
    Deletes a single contact from a specified mailing list.

    Args:
        base_url (str): Qualtrics base URL (e.g., https://{data_center}.qualtrics.com).
        token (str): OAuth2 bearer token with `write:mailing_list_contacts` scope.
        directory_id (str): Directory ID (POOL_...).
        mailing_list_id (str): Mailing List ID (CG_...).
        contact_id (str): Contact ID (CID_...).

    Returns:
        dict: JSON response containing the status of the deletion.
    """
    endpoint_url = f"{base_url}/API/v3/directories/{directory_id}/mailinglists/{mailing_list_id}/contacts/{contact_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.delete(endpoint_url, headers=headers)
    return response.json()
