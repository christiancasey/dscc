#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 2019

@author: christiancasey

This loads the title list. MORE INFO HERE
"""

import os
import glob
import re
import pandas

#%% Load data file

# Get the current titles list from the CSV file that Jasmine is editing
strURL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRn0p05_7FUCxadsu4EXAHrQ-s18Xg_xpCZHjy9mdrJbxkf8P448_bnCxNuOdPaOI9BKp1frhHplugk/pub?output=csv'
dfSheet = pandas.read_csv(strURL)

# Select only those titles marked for upload
dfTitles = dfSheet.loc[dfSheet['Upload']==1]


#%% Get file list for PDFs
vFiles = glob.glob('pdf_in/*.pdf')
for strFilename in vFiles:
	print(strFilename)


