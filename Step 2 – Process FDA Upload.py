#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 12:43:18 2019

@author: christiancasey

Step 1
Download metadata, create thumbnails, add cover page, create SAF, zip.
Result is a single zip file: SimpleArchiveFormat.zip
"""


import os
import shutil
import glob
import re
import pandas
import pygsheets

#%% Function definitions


# Eliminate junk before and after entries
def CleanCellString(strCell):
	strCell = re.sub(r'^\W*', '', strCell)
	strCell = re.sub(r'\W*$', '', strCell)
	return strCell


# Combine both Latin and non-Latin data where available
def CombineLatOrg(strLat, strOrg):
	strLat = strLat.strip()
	strOrg = strOrg.strip()
	
	if len(strLat) > 0 and len(strOrg) > 0:
		return strOrg + ' – ' + strLat
	
	return strOrg + strLat


# Create thumbnail file name from PDF file name
def ThumbFileName(strPDF):
	return re.sub(r'\.pdf$', '_thumb.png', strPDF)


# Helper functions for applys

def MakeAnchor(strURL):
	if strURL:
		strURL = strURL.strip()
		if strURL:
			return "<a href='" + strURL + "'>" + strURL + "</a>"


def MakeOCLC(strID):
	if strID:
		strID = strID.strip()
		if strID:
			return "<a href='http://www.worldcat.org/oclc/" + strID + "'>OCLC: " + strID + "</a>"


def MakeRelationFull(string):
	if string:
		temp = string
		temp = temp.replace('http://hdl.handle.net/','full:001:https://archive.nyu.edu/bitstream/')
		temp = temp.replace('|','/1/')
		return temp	


def MakeRelationThumb(string):
	if string:
		temp = string
		temp = temp.replace('http://hdl.handle.net/','thumb:001:https://archive.nyu.edu/bitstream/')
		temp = temp.replace('|','/2/')
		temp = temp.replace('.pdf','_thumb.png')
		return temp


# Removes the appended number from column names where necessary
def TruncateFinalNumber(s):
	if isinstance(s,str):
		if any(c.isdigit() for c in s):
			return s[:-1]
	return s

#%% Load metadata files

# Get the upload data from the metadata CSV, which was created from the Google Sheet in Step 1
dfTitles = pandas.read_csv('FDA_upload.csv')
dfTitles = dfTitles.fillna('')

# Select only those titles marked for upload, which have rights information present
dfTitlesUpload = dfTitles
dfTitlesUpload = dfTitlesUpload.loc[dfTitlesUpload['Upload'] == 1]
dfTitlesUpload = dfTitlesUpload.loc[dfTitlesUpload['Rights information'] != '']
#dfTitlesUpload = dfTitlesUpload.loc[dfTitlesUpload['FDA Handle'] == '']
#iUploadRows = (dfTitles['Upload'] == 1) & (dfTitles['Rights information'] != '') #& (dfTitles['FDA Handle'] == '')
iUploadRows = dfTitles['FDA Item'] != ''

# Get the map from mapfile and format it as a dict
with open('mapfile', 'r') as f:
	strMap = f.read()
	f.close()

vMap = strMap.strip().split('\n')
vMap = [s.split(' ') for s in vMap]
dMap = {v[0]: v[1] for v in vMap}


#%% Link handles from mapfile in new column

# Add some empty columns for the new data
dfOmeka = dfTitles.copy()
#dfOmeka['Handle URI'] = pandas.Series()
#dfOmeka = dfOmeka.fillna('')

for i, dfRow in dfOmeka.iterrows():
	
	# The item is necessary for confirming the match between the FDA item and the URL
	strItem = CleanCellString(dfRow['FDA Item'])
	
	# Skip this row if there is no FDA item entry
	if strItem:
		dfRow['FDA Handle'] = MakeAnchor('http://hdl.handle.net/' + dMap[strItem])
		dfRow['OCLC'] = MakeOCLC( dfRow['OCLC'] )
	

#% Rearrange the data frame to include Dublin Core columns in proper combinations

# Get the Dublin Core identifiers and the current column list
vColumns = [item for item in dfTitles.iloc[[1]].values.tolist()[0]]
iColumns = [i for i, item in enumerate(vColumns) if item != '']

# Select only columns with Dublin Core names
dfOmeka = dfOmeka.iloc[:,iColumns]
## Rename columns to Dublin Core names
dfOmeka.columns = [item for item in vColumns if item != '']

#% Concatenate columns

dfOmeka['Dublin Core:Relation1'] = dfOmeka.iloc[:, 0] + '|' + dfOmeka['Dublin Core:Relation']
dfOmeka['Dublin Core:Relation2'] = dfOmeka.iloc[:, 0] + '|' + dfOmeka['Dublin Core:Relation']
dfOmeka['Dublin Core:Relation1'] = dfOmeka['Dublin Core:Relation1'].apply(lambda x: MakeRelationFull(x))
dfOmeka['Dublin Core:Relation2'] = dfOmeka['Dublin Core:Relation2'].apply(lambda x: MakeRelationThumb(x))


dfOmeka['Dublin Core:Identifier_'] = dfOmeka['Dublin Core:Identifier'].apply(lambda x: '|'.join(filter(None, x)), axis=1)
dfOmeka['Dublin Core:Title_'] = dfOmeka['Dublin Core:Title'].apply(lambda x: '|'.join(filter(None, x)), axis=1)
dfOmeka['Dublin Core:Creator_'] = dfOmeka['Dublin Core:Creator'].apply(lambda x: '|'.join(filter(None, x)), axis=1)
dfOmeka['Dublin Core:Publisher_'] = dfOmeka['Dublin Core:Publisher'].apply(lambda x: '|'.join(filter(None, x)), axis=1)
dfOmeka['Dublin Core:Description_'] = dfOmeka['Dublin Core:Description'].apply(lambda x: '|'.join(filter(None, x)), axis=1)
dfOmeka['Dublin Core:Coverage_'] = dfOmeka['Dublin Core:Coverage'].apply(lambda x: '|'.join(filter(None, x)), axis=1)
dfOmeka['Dublin Core:Relation_'] = dfOmeka[['Dublin Core:Relation1', 'Dublin Core:Relation2']].apply(lambda x: '|'.join(filter(None, x)), axis=1)


vNewCols = ['Dublin Core:Relation_', 'Dublin Core:Type', 'Dublin Core:Date', 'Dublin Core:Extent', 'Dublin Core:Subject', 'Dublin Core:Rights', 'Dublin Core:Language', 'Dublin Core:Identifier_', 'Dublin Core:Title_', 'Dublin Core:Creator_', 'Dublin Core:Publisher_', 'Dublin Core:Description_', 'Dublin Core:Coverage_']


dfOmekaUpload = dfOmeka
dfOmekaUpload = dfOmekaUpload[vNewCols]
dfOmekaUpload = dfOmekaUpload[iUploadRows]
dfOmekaUpload.columns = dfOmekaUpload.columns.astype(str).str.replace("_", "")
dfOmekaUpload = dfOmekaUpload.reset_index(drop=True)


# Reduce columns to FDA import
#cols = [item for item in dcaa.iloc[[2]].values.tolist()[0]] # Get list of FDA headers
#cols_index = [cols.index(item) for item in cols if item != ''] # Get index of headers and remove unnecessary columns
#fda = dcaa[cols_index]
vDC = [item for item in dfTitles.iloc[[1]].values.tolist()[0]]  # Get list of FDA headers
vDCOriginal = [TruncateFinalNumber(s) for s in vDC]

vOmekaColumns = [c for c in dfOmekaUpload.columns if c in vDCOriginal]
	
dfOmekaUpload = dfOmekaUpload[omeka_cols]

dfOmekaUpload.to_csv('./omeka_import.csv', sep=',', index=False)







