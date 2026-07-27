# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 10:25:08 2025

@author: Kieran Martin
"""
from setuptools import setup

# read your requirements.txt, if you like
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="qualtrics_api_program",
    version="0.1.0",
    py_modules=["analysis", "qual_api", "report", "utils"],
    install_requires=requirements,
)

