# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 11:07:04 2026

@author: kieranmartin
"""
import requests
import pandas as pd
import numpy as np
import re

def strip_html(data):
    """
    Remove HTML tags from the input data, which may be a string, list, or dictionary.
    
    Args:
        data (str, list, or dict): The data from which HTML tags should be stripped.
    
    Returns:
        The same data structure with HTML tags removed from strings.
    """
    html_pattern = re.compile(r'<[^>]*>')
    if isinstance(data, str):
        return html_pattern.sub('', data)
    elif isinstance(data, dict):
        return {k: strip_html(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [strip_html(item) for item in data]
    else:
        return data


def subset_by_date_range(responses_df, start_date, end_date):
    """
    Subset the responses DataFrame based on a specified date range.

    This function filters the `responses_df` DataFrame to include only rows 
    where the 'recordedDate' column falls within the specified `start_date` and 
    `end_date` range. The 'recordedDate' column must be in a timezone-aware 
    datetime format (UTC). The function will automatically convert `start_date` 
    and `end_date` to UTC if they are timezone-naive.

    Parameters:
    ----------
    responses_df : pd.DataFrame
        The DataFrame containing survey responses with a 'recordedDate' column 
        in ISO format.
    start_date : str or datetime-like
        The start of the date range, inclusive. It should be in a format 
        compatible with `pd.to_datetime`.
    end_date : str or datetime-like
        The end of the date range, inclusive. It should be in a format 
        compatible with `pd.to_datetime`.

    Returns:
    -------
    pd.DataFrame
        A subset of `responses_df` where the 'recordedDate' is within the 
        specified date range.
        
    Example:
    -------
    >>> responses_df = subset_by_date_range(responses_df, '2024-06-27', '2024-07-08')
    """

    # Ensure the 'recordedDate' column is in datetime format and set to UTC if needed
    responses_df['recordedDate'] = pd.to_datetime(responses_df['recordedDate']).dt.tz_convert('UTC')

    # Convert the start and end dates to datetime with UTC timezone
    start_date = pd.to_datetime(start_date).tz_localize('UTC')
    end_date = pd.to_datetime(end_date).tz_localize('UTC')
    
    # Subset the DataFrame based on the date range
    subset_df = responses_df[(responses_df['recordedDate'] >= start_date) & (responses_df['recordedDate'] <= end_date)]
    
    return subset_df


