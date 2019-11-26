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
import pygsheets

#%% Load data file

# Get the current titles list from the CSV file that Jasmine is editing
strURL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRn0p05_7FUCxadsu4EXAHrQ-s18Xg_xpCZHjy9mdrJbxkf8P448_bnCxNuOdPaOI9BKp1frhHplugk/pub?output=csv'
dfTitles = pandas.read_csv(strURL)
dfTitles = dfTitles.fillna('')

# Select only those titles marked for upload
dfTitlesUpload = dfTitles.loc[dfTitles['Upload']==1]

#%%

dfTitles.loc[ dfTitles['Original Filename'] == dfTitlesUpload['Original Filename'].iloc[0], 'Omeka Link'] = 'test'

#%% Get file list for PDFs
vFiles = glob.glob('pdf_in/*.pdf')
for strFilename in vFiles:
	print(strFilename)



#%% Google Sheets test
gc = pygsheets.authorize(service_file='credentials.json')

sh = gc.open('DSCC Title List')
wks = sh[0]
wks.set_dataframe(dfTitles,(1,1))



