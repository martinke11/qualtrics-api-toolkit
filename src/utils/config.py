# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 10:05:19 2025

@author: Kieran Martin
"""
import os
import json

from functions import (
    set_project_directory,
    get_qualtrics_credentials_path
)

PROJECT_DIRECTORY = set_project_directory()
print("Working directory changed to:", PROJECT_DIRECTORY)

QUALTRICS_CREDENTIALS_PATH = get_qualtrics_credentials_path()
print("Qualtrics credentials path:", QUALTRICS_CREDENTIALS_PATH)

with open(QUALTRICS_CREDENTIALS_PATH) as f:
    QUALTRICS_CREDS = json.load(f)

BASE_URL = f'https://{QUALTRICS_CREDS.get("DataCenter")}.qualtrics.com'
