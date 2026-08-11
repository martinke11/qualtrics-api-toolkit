# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 11:07:04 2026

@author: kieranmartin

NOTE: "Distributions" here refers to sms distributions only, which is why naming
includes "sms" to specify )e.g. "create_sms_distribution"). The other endpoint
called "Distributions" is for email distributions. Please see "distributions.py"
"""
import requests
import json

# SMS Distributions:
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
    endpoint_url = f"{base_url}/API/v3/distributions/sms"
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

    resp = requests.post(endpoint_url, headers=headers, json=payload, timeout=16)

    try:
        resp.raise_for_status()
    except requests.HTTPError:
        print("=== REQUEST PAYLOAD ===")
        print(json.dumps(payload, indent=2))
        print("\n=== RESPONSE ===")
        print(resp.status_code, resp.text)
        raise

    return resp.json()


def list_SMS_distribution(
    base_url,
    token,
    survey_id,
    page_size=None,
    skip_token=None,
):
    '''
    '''
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

    
def get_sms_distribution(base_url, token, sms_distribution_id, survey_id):
    '''
    '''
    endpoint_url = f"{base_url}/API/v3/distributions/sms/{sms_distribution_id}"
    params = {
        "surveyId": survey_id, 
        "smsDistributionId": sms_distribution_id
    }
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(endpoint_url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def delete_SMS_distribution(base_url, token, sms_distribution_id, survey_id):
    '''
    '''
    endpoint_url = f"{base_url}/API/v3/distributions/sms/{sms_distribution_id}"
    params = {
        "surveyId": survey_id, 
        "smsDistributionId": sms_distribution_id
    }
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.delete(endpoint_url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()
