# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 09:57:25 2026

@author: kieranmartin
"""
import requests

# Survey Responses --> Surveys/Response Import/Export API --> Response Exports
def start_response_export(base_url, token, survey_id):
    """
    Initiates the export of survey responses from Qualtrics.

    Args:
        base_url (str): The base URL for the Qualtrics API.
        access_token (str): The bearer access token for API authorization.
        survey_id (str): The unique ID of the survey whose responses are to be 
                         exported.

    Returns:
        dict: A JSON-formatted response containing the export details, such as 
              progress and file ID.
    """
    # Set the survey export URL
    endpoint_url = f'{base_url}/API/v3/surveys/{survey_id}/export-responses'
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    # Pull the survey data
    response = requests.post(
        endpoint_url, 
        headers=headers,
        data='{"format": "json", "compress": false}'
    )
    # Convert the data into a more readable format
    response = response.json()    
    return response


def get_response_export_progress(base_url, token, survey_id, export_progress_id):
    """
    Checks the progress of an ongoing survey response export.

    Args:
        base_url (str): The base URL for the Qualtrics API.
        access_token (str): The bearer access token for API authorization.
        survey_id (str): The unique ID of the survey whose responses are being 
                         exported.
        export_progress_id (str): Export progressId returned by the start export 
        call. unique ID representing the current export progress. 

    Returns:
        dict: A JSON-formatted response indicating the progress status and 
        completion percentage.
    """
    endpoint_url = (
        f"{base_url}/API/v3/surveys/{survey_id}"
        f"/export-responses/{export_progress_id}"
    )
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


# helper function for calling get_response_export_progress
def wait_for_export_completion(base_url, token, survey_id, export_progress_id):
    """
    Waits for the survey response export to complete by checking its progress.
    Helper function for calling get_response_export_progress.
    
    Args:
        base_url (str): The base URL for the Qualtrics API.
        token (str): The API token used for authorization.
        survey_id (str): The ID of the survey being exported.
        export_progress_id (str): The progress ID of the ongoing export.

    Returns:
        str: The file ID (file_id) when the export is complete.
    """
    # Initialize the file ID to empty
    file_id = ""
    
    # Loop until the export is complete and the file ID is available
    while len(file_id) == 0:
        # Check the progress of the export
        response_export_progress = get_response_export_progress(
            base_url, 
            token, 
            survey_id, 
            export_progress_id
        )

        # Check if the export is 100% complete
        if response_export_progress.get('result').get('percentComplete') == 100:
            # Check if the status is 'complete'
            if response_export_progress.get('result').get('status') == 'complete':
                # Get the file ID
                file_id = response_export_progress.get('result').get('fileId')
            else:
                print("Status: " + response_export_progress.get('result').get('status'))
    
    return file_id


def get_response_export_file(base_url, token, survey_id, file_id):
    """
    Downloads the survey responses after the export process is complete.

    Args:
        base_url (str): The base URL for the Qualtrics API.
        access_token (str): The bearer access token for API authorization.
        survey_id (str): The unique ID of the survey whose responses are to be 
                        downloaded.
        file_id (str): The file ID representing the exported survey responses.

    Returns:
        requests.Response: The HTTP response containing the survey responses file.
    """
    endpoint_url = (
        f"{base_url}/API/v3/surveys/{survey_id}"
        f"/export-responses/{file_id}/file"
    )
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    response = requests.get(
        endpoint_url, 
        headers=headers
    )
    
    return response


def get_list_of_available_filters():
    '''
    '''
    return






