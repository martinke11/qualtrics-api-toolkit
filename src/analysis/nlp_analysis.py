#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 10:22:33 2024

@author: kieranmartin
"""
import pandas as pd
import warnings
# nltk.download('all') # nltk.download('vader_lexicon')

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
warnings.simplefilter(action='ignore', category=pd.errors.DtypeWarning)

# Ensure that all output is printed without truncation
pd.options.mode.chained_assignment = None 
pd.set_option('display.max_colwidth', None)  # Do not truncate column content
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns

from src.utils import QUALTRICS_CREDS

    
# build out from here 
