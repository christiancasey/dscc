#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 2019

@author: christiancasey

This loads the title list. This is a test run to verify reading and writing from Google Sheet.
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
dfTitlesUpload = dfTitlesUpload.sort_values(['Filename'])

#%% Make sure files are actually present

vFiles = dfTitlesUpload['Filename'].tolist()
for strFile in vFiles:
	try:
		f = open('pdf_in/' + strFile)
	except:
		raise Warning('%s not found.' % strFile)
		

#%% Change something to test

dfTitles.loc[ dfTitles['Original Filename'] == dfTitlesUpload['Original Filename'].iloc[0], 'Omeka Link'] = 'test'




#%% Update Google Sheet with new data
gc = pygsheets.authorize(service_file='credentials.json')

sh = gc.open('DSCC Title List')
wks = sh[0]
#wks.set_dataframe(dfTitles,(1,1))



