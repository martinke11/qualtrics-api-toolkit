# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 09:49:28 2026

@author: kieranmartin
"""
import requests
import pandas as pd
from .utils import strip_html
import requests
import pandas as pd
import numpy as np
import re


def get_survey_questions(base_url, token, survey_id):
    """
    Retrieve the questions from a specific survey in the Qualtrics API and 
    clean the data by stripping HTML tags.

    uses strip_html in utils.py
    
    This function fetches the survey questions from a specified survey using 
    the Qualtrics API. It returns the survey data as a dictionary and removes 
    any HTML tags that may be present in the survey question text.

    Args:
        base_url (str): The base URL for the Qualtrics API.
    token (str): The API token used for authorization.
        survey_id (str): The unique ID of the survey whose questions are 
        being retrieved.

    Returns:
        dict: A dictionary containing the survey questions with HTML tags removed.
        
    Raises:
        requests.exceptions.RequestException: If there's an error with the API request.
    """
    # Set the URL for the specific survey
    endpoint_url = f'{base_url}/API/v3/surveys/{survey_id}'
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(
        endpoint_url, 
        headers=headers
    )
    survey_question_dictionary = response.json()

    # Apply HTML cleaning on the survey questions inside 'result'
    if (
        'result' in survey_question_dictionary
        and 'questions' in survey_question_dictionary['result']
    ):
        for question_id, question_data in (
            survey_question_dictionary['result']['questions'].items()
        ):
            if 'questionText' in question_data:
                question_data['questionText'] = (
                    strip_html(question_data['questionText']).strip()
                )
            if 'choices' in question_data:
                question_data['choices'] = strip_html(question_data['choices'])
            
    return survey_question_dictionary


def get_survey_list(base_url, token):
    """
    Retrieve a complete list of surveys from the Qualtrics API, handling 
    pagination if necessary.
    
    This function makes repeated API requests to the Qualtrics survey endpoint 
    to retrieve all surveys.It handles the pagination of results by checking 
    for a "nextPage" key in the API response, which provides an offset for 
    subsequent pages of data. The function returns the complete survey list in 
    the form of a Pandas DataFrame.
    
    Args:
        base_url (str): The base URL for the Qualtrics API.
        token (str): The API token used for authorization.

    Returns:
        pd.DataFrame: A DataFrame containing the complete list of surveys 
        with their details.
        
    Raises:
        requests.exceptions.RequestException: If there's an error with the 
        API request.
    """
    # Initialize the flag to track pagination and the offset for next pages
    flag = True
    count = 0
    offset = ""
    
    while flag:
        # Determine the URL based on whether it's the first page or a subsequent page
        if count == 0:
            endpoint_url = f'{base_url}/API/v3/surveys'
        else:
            endpoint_url = f'{base_url}/API/v3/surveys?offset={offset}'
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        # Make the API request
        response = requests.get(
            endpoint_url, 
            headers=headers
        )
        response_json = response.json()

        # Extract the current page of survey results into a DataFrame
        current_page_df = pd.DataFrame(response_json.get("result").get("elements"))
        
        # For the first page, initialize the DataFrame; for others, append to it
        if count == 0:
            survey_list_df = current_page_df
        else:
            survey_list_df = pd.concat([survey_list_df, current_page_df])
            
        # Check if there's a next page and update flag and offset accordingly
        if response_json.get("result").get("nextPage") is None:
            flag = False
        else:
            next_page_str = response_json.get("result").get("nextPage")
            offset = next_page_str.split("?offset=", 1)[1]
            count += 1
    
    # Reset the indices of the final DataFrame and return it
    survey_list_df = survey_list_df.reset_index(drop=True)
    
    return survey_list_df


import tkinter as tk
from tkinter import ttk


def select_survey(survey_list_df):
    """
    Display a popup dropdown for selecting a survey.

    Parameters
    ----------
    survey_list_df : pd.DataFrame
        DataFrame containing available survey names.

    Returns
    -------
    str
        The name of the selected survey.
    """
    root = tk.Tk()
    root.title("Select Survey")
    root.geometry("500x120")

    survey_name = tk.StringVar()

    tk.Label(
        root,
        text="Select a survey:"
    ).pack(pady=(10, 5))

    survey_dropdown = ttk.Combobox(
        root,
        textvariable=survey_name,
        values=survey_list_df["name"].tolist(),
        state="readonly",
        width=60
    )
    survey_dropdown.pack(pady=5)
    survey_dropdown.current(0)

    tk.Button(
        root,
        text="Select",
        command=root.destroy
    ).pack(pady=5)

    root.mainloop()

    return survey_name.get()


def get_survey_id_by_name(survey_list_df, survey_name):
    """
    Retrieves the survey ID based on the survey name from a DataFrame.

    Args:
        survey_list_df (pd.DataFrame): A DataFrame containing survey data with 
                                       'name' and 'id' columns.
        survey_name (str): The name of the survey to search for.

    Returns:
        str: The survey ID if found, or None if not found or multiple surveys 
             have the same name.
    """
    # Pull the indices associated with the Survey Name
    survey_name_indices = survey_list_df.loc[survey_list_df['name'] == survey_name].index[:]
    
    if len(survey_name_indices) > 1:
        print('Multiple Surveys Have the Same Name!!!')
        return None  # Return None to indicate multiple surveys found
    elif len(survey_name_indices) == 0:
        print('Cannot Find the Survey. Please Check that the Survey Name is Correct.')
        return None  # Return None to indicate survey not found
    else:
        # Return the survey ID using the survey index
        survey_id = survey_list_df.loc[survey_name_indices[0], 'id']
        return survey_id


def update_survey(base_url, token, survey_id, data):
    """
    Updates a survey's details.

    Args:
        base_url (str): Base URL for the API.
        access_token (str): Access token for authentication.
        survey_id (str): Survey ID.
        data (dict): Data to update.

    Returns:
        dict: Response from the API.
    """
    endpoint_url = f'{base_url}/API/v3/surveys/{survey_id}'
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    response = requests.put(
        endpoint_url,
        headers=headers,
        data=data
    )
    
    return response.json()


def share_survey(base_url, token, survey_id, recipient_id, permissions):
    """
    Shares a survey with another user in your brand.

    Args:
        base_url (str): Qualtrics base URL (e.g., https://{data_center}.qualtrics.com).
        token (str): Your Qualtrics API token.
        survey_id (str): The unique identifier for the survey (e.g., SV_...).
        recipient_id (str): The userId or groupId the survey is shared with.
        permissions (dict): The permissions object specifying the various permissions being assigned.

    Returns:
        dict: JSON response from the API.
    """
    endpoint_url = f"{base_url}/surveys/{survey_id}/permissions/collaborations"
    data = {
        "recipientId": recipient_id,
        "permissions": permissions
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-TOKEN": token
    }
    
    response = requests.post(
        endpoint_url, 
        headers=headers, 
        json=data
    )
    
    return response.json()


