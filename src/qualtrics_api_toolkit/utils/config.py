# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 10:05:19 2025

@author: Kieran Martin
"""
import json
from pathlib import Path

from .functions import get_qualtrics_credentials_path


QUALTRICS_CREDENTIALS_PATH = Path(
    get_qualtrics_credentials_path()
).expanduser().resolve()

with QUALTRICS_CREDENTIALS_PATH.open(
    mode="r",
    encoding="utf-8",
) as file:
    QUALTRICS_CREDS = json.load(file)

DATA_CENTER = QUALTRICS_CREDS["DataCenter"]
BASE_URL = f"https://{DATA_CENTER}.qualtrics.com"

# Method below for using the Repository Without Installing the Package:
# import os
# import json
# from pathlib import Path

# from .functions import (
#     set_project_directory,
#     get_qualtrics_credentials_path
# )

# PROJECT_DIRECTORY = set_project_directory()
# print("Working directory changed to:", PROJECT_DIRECTORY)

# QUALTRICS_CREDENTIALS_PATH = get_qualtrics_credentials_path()
# print("Qualtrics credentials path:", QUALTRICS_CREDENTIALS_PATH)

# with open(QUALTRICS_CREDENTIALS_PATH) as f:
#     QUALTRICS_CREDS = json.load(f)

# BASE_URL = f'https://{QUALTRICS_CREDS.get("DataCenter")}.qualtrics.com'
