import requests
import json

def list_distribution_history(
    base_url,
    token,
    distribution_id,
    skip_token=None
):
    """
    Retrieves a list showing the distribution history for a specific 
    distribution from Qualtrics.
    
    Note: This API endpoint is only supported for users on XM Directory 
          (not for Genesis Contacts).

    Args:
        base_url (str): The base URL of your Qualtrics data center 
                        (e.g., 'https://yul1.qualtrics.com').
        api_token (str): API token for authentication (provided in 
                        the X-API-TOKEN header).
        distribution_id (str): The ID for the desired distribution
                                (e.g., 'EMD_1234567890abcde').
        skip_token (str, optional): The start position for pagination when 
                                    using pagination.

    Returns:
        dict: JSON response from the Qualtrics API, typically including:
            {
                "result": {
                    "elements": [...],
                    "nextPage": "string or null"
                },
                "meta": {
                    "httpStatus": "string",
                    "requestId": "string",
                    "notice": "string"
                }
            }
    """
    endpoint_url = f"{base_url}/API/v3/distributions/{distribution_id}/history"

    params = {"distributionId": distribution_id}
    if skip_token:
        params["skipToken"] = skip_token

    headers = {
        "Accept": "application/json",
        "X-API-TOKEN": token
    }


    response = requests.get(endpoint_url, headers=headers, params=params)
    response.raise_for_status()  
    return response.json()


def list_SMS_distribution(
        base_url,
        token,
        survey_id,
        page_size=None,
        skip_token=None,
    ):
    endpoint_url = f"{base_url}/API/v3/distributions/sms"
    params = {"surveyId": survey_id}
    if page_size is not None:
        params["pageSize"] = page_size
    if skip_token:
        params["skipToken"] = skip_token

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(endpoint_url, headers=headers, params=params)
    response.raise_for_status()  # optional: raise an exception for 4xx/5xx status codes
    return response.json()

    
def delete_SMS_distribution(base_url, token, sms_distribution_id, survey_id):
    endpoint_url = f"{base_url}/API/v3/distributions/sms/{sms_distribution_id}"
    params = {"surveyId": survey_id, "smsDistributionId": sms_distribution_id}
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.delete(endpoint_url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def delete_email_distribution(base_url, token, distribution_id):
    endpoint_url = f"{base_url}/API/v3/distributions/{distribution_id}"
    params = {"distributionId": distribution_id}
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.delete(endpoint_url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def list_distributions(
    base_url,
    token,
    survey_id,
    distribution_request_type=None,
    mailing_list_id=None,
    offset=None,
    page_size=None,
    send_end_date=None,
    send_start_date=None,
    skip_token=None,
    use_new_pagination_scheme=None
):
    """
    Retrieves a list of distributions for a particular survey from Qualtrics.

    Args:
        base_url (str): The base URL of your Qualtrics data center 
                        (e.g., 'https://{data_center}.qualtrics.com').
        token (str): OAuth2 bearer token with 'read:distributions' scope.
        survey_id (str): The survey ID to which distributions are related (e.g., 'SV_123abc').
        distribution_request_type (str, optional):
            The distribution type to filter by. Possible values:
            'Invite', 'ThankYou', 'Reminder', 'Email', 'Portal', 'PortalInvite', 'GeneratedInvite'.
        mailing_list_id (str, optional):
            The mailing list or contact group associated with the distribution(s).
        offset (int, optional):
            The starting offset for the pagination (deprecated, but still supported).
        page_size (int, optional):
            The maximum number of distributions to return per request (1–100).
        send_end_date (str, optional):
            Ending range on the distribution send date (e.g., '2020-07-21T17:32:28Z').
        send_start_date (str, optional):
            Starting range on the distribution send date (e.g., '2020-07-20T17:32:28Z').
        skip_token (str, optional):
            The start position for pagination when using the new pagination scheme.
        use_new_pagination_scheme (bool, optional):
            Whether to enable the new string-based pagination functionality.

    Returns:
        dict: JSON response from the Qualtrics API. Typically contains:
            {
                "result": {
                    "elements": [...],
                    "nextPage": "string or null"
                },
                "meta": {
                    "httpStatus": "string",
                    "requestId": "string",
                    "notice": "string"
                }
            }
    """
    endpoint_url = f"{base_url}/API/v3/distributions"

    # Build query parameters
    params = {"surveyId": survey_id}
    if distribution_request_type:
        params["distributionRequestType"] = distribution_request_type
    if mailing_list_id:
        params["mailingListId"] = mailing_list_id
    if offset is not None:
        params["offset"] = offset
    if page_size is not None:
        params["pageSize"] = page_size
    if send_end_date:
        params["sendEndDate"] = send_end_date
    if send_start_date:
        params["sendStartDate"] = send_start_date
    if skip_token:
        params["skipToken"] = skip_token
    if use_new_pagination_scheme is not None:
        # Must convert boolean to lowercase string for query parameter (True -> 'true')
        params["useNewPaginationScheme"] = str(use_new_pagination_scheme).lower()

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(endpoint_url, headers=headers, params=params)
    response.raise_for_status() 
    return response.json()
        

def create_sms_distribution(
    base_url: str,
    token: str,
    survey_id: str,
    name: str,
    send_date: str,
    mailing_list_id: str | None,
    contact_id: str | None,
    sample_id: str | None,
    transaction_batch_id: str | None,
    transaction_id: str | None,
    library_id: str | None,
    message_id: str | None,
    message_text: str | None,
    parent_distribution_id: str | None,
    survey_link_expiration_date: str | None,
    method: str = "Invite",
) -> dict:
    """
    Create a survey SMS distribution in Qualtrics using OAuth2 Bearer auth.

    Args:
        base_url: Qualtrics base URL, e.g. "https://yourdatacenter.qualtrics.com"
        token: OAuth2 Bearer token with write:distributions scope
        survey_id: Survey ID to distribute (e.g. "SV_xxx")
        name: Name for the SMS distribution (<=100 chars)
        send_date: ISO8601 send date/time (required)
        method: "Invite", "Interactive", "Reminder", or "Thankyou"
        mailing_list_id: Mailing List ID for batch distribution
        contact_id: Contact Lookup ID for individual distribution
        sample_id: Sample ID (subgroup of mailing list)
        transaction_batch_id: Transaction Batch ID
        transaction_id: Transaction ID
        library_id: Library ID of an SMS message (e.g. "UR_xxx")
        message_id: Message ID in that library (e.g. "MS_xxx")
        message_text: Custom SMS text (<=10,000 chars)
        parent_distribution_id: For Reminder/Thankyou, the parent SMS distribution ID
        survey_link_expiration_date: ISO8601 expiration for the survey link

    Returns:
        Parsed JSON response from Qualtrics (dict).
    """
    url = f"{base_url}/API/v3/distributions/sms"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "surveyId": survey_id,
        "name": name,
        "sendDate": send_date,
        "method": method,
        "recipients": {}
    }

    # Recipients for Invite/Interactive
    if method not in ("Reminder", "Thankyou"):
        if transaction_batch_id:
            payload["recipients"]["transactionBatchId"] = transaction_batch_id
        elif mailing_list_id:
            payload["recipients"]["mailingListId"] = mailing_list_id
            if contact_id:
                payload["recipients"]["contactId"] = contact_id
            if sample_id:
                payload["recipients"]["sampleId"] = sample_id
            if transaction_id:
                payload["recipients"]["transactionId"] = transaction_id
        else:
            raise ValueError(
                "For Invite/Interactive you must supply transaction_batch_id or mailing_list_id"
            )

    # Message for Invite/Reminder/Thankyou
    if method in ("Invite", "Reminder", "Thankyou"):
        payload["message"] = {}
        if library_id and message_id:
            payload["message"]["libraryId"] = library_id
            payload["message"]["messageId"] = message_id
        elif message_text:
            payload["message"]["messageText"] = message_text
        else:
            raise ValueError(
                "For Invite/Reminder/Thankyou you must supply library_id & message_id or message_text"
            )

    # Parent distribution (Reminder/Thankyou)
    if parent_distribution_id:
        payload["parentDistributionId"] = parent_distribution_id

    # Link expiration
    if survey_link_expiration_date:
        payload["surveyLinkExpirationDate"] = survey_link_expiration_date

    resp = requests.post(url, headers=headers, json=payload, timeout=16)

    try:
        resp.raise_for_status()
    except requests.HTTPError:
        print("=== REQUEST PAYLOAD ===")
        print(json.dumps(payload, indent=2))
        print("\n=== RESPONSE ===")
        print(resp.status_code, resp.text)
        raise

    return resp.json()


def create_email_distribution(
    base_url: str,
    token: str,
    library_id: str,
    message_id: str,
    survey_id: str,
    mailing_list_id: str | None,
    contact_id: str | None,
    directory_id: str | None,
    transaction_batch_id: str | None,
    from_email: str | None,
    reply_to_email: str | None,
    from_name: str | None,
    subject: str | None,
    expiration_date: str | None,
    distribution_type: str | None,
    send_date: str | None
) -> dict:
    """
    Create a survey email distribution in Qualtrics using OAuth2-style Bearer token
    (same header style as list_distributions).

    Raises and prints the full response body on HTTP error for easier debugging.
    """
    url = f"{base_url}/API/v3/distributions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "message": {
            "libraryId": library_id,
            "messageId": message_id
        },
        "recipients": {},
        "header": {},
        "surveyLink": {
            "surveyId": survey_id
        }
    }

    # recipients
    if mailing_list_id:
        payload["recipients"]["mailingListId"] = mailing_list_id
    if contact_id:
        payload["recipients"]["contactId"] = contact_id
    if directory_id:
        payload["recipients"]["directoryId"] = directory_id
    if transaction_batch_id:
        payload["recipients"]["transactionBatchId"] = transaction_batch_id

    # header
    if from_email:
        payload["header"]["fromEmail"] = from_email
    if reply_to_email:
        payload["header"]["replyToEmail"] = reply_to_email
    if from_name:
        payload["header"]["fromName"] = from_name
    if subject:
        payload["header"]["subject"] = subject

    # surveyLink details
    if expiration_date:
        payload["surveyLink"]["expirationDate"] = expiration_date
    if distribution_type:
        payload["surveyLink"]["type"] = distribution_type

    # optional send date
    if send_date:
        payload["sendDate"] = send_date

    resp = requests.post(url, headers=headers, json=payload)

    try:
        resp.raise_for_status()
    except requests.HTTPError:
        print("=== REQUEST PAYLOAD ===")
        print(json.dumps(payload, indent=2))
        print("\n=== RESPONSE ===")
        print(resp.status_code, resp.text)
        raise

    return resp.json()

