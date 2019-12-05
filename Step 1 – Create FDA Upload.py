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
from PyPDF2 import PdfFileMerger

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


# Generate the dublin_core.xml for each file's metadata
def GenerateDublinCoreXML(df):
	strXML = '<?xml version="1.0" encoding="UTF-8"?><dublin_core>'
	
	# Loop through columns and add to XML
	for (strName, strData) in df.iteritems():
		
		# Strip out string from pandas data
		strData = strData.values[0].strip()
		
		strValue = '<dcvalue'
		# If the identifier contains a dot, split it into element and qualifier
		iDotLoc = strName.find('.')
		if iDotLoc >= 0:
			strElement = strName[0:iDotLoc]
			strQualifier = strName[(iDotLoc + 1):]
			strValue = strValue + ' element="' + strElement + '"' + ' qualifier="' + strQualifier + '"'
		else:
			strValue = strValue + ' element="' + strName + '"'
		
		strValue = strValue + '>' + strData + '</dcvalue>'
		strXML = strXML + strValue
		
	strXML = strXML + '</dublin_core>'
	return strXML


#%% Prepare temporary directories for content

# Delete everything in the directory: pdf_out
if os.path.exists('./pdf_out'):
	shutil.rmtree('./pdf_out')
os.mkdir('pdf_out')
	
# Delete everything in the directory: tex_out
if os.path.exists('./tex_out'):
	shutil.rmtree('./tex_out')
os.mkdir('tex_out')
	
# Copy everything in the coverpage directory to tex_out
vFiles = glob.glob('./coverpage/*')
for strFile in vFiles:
	strFile = strFile.replace('./coverpage/', '')
	os.system('cp "coverpage/%s" ./tex_out/' % strFile)


#%% Load metadata file

# Get the current titles list from the CSV file that Jasmine is editing
strURL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRn0p05_7FUCxadsu4EXAHrQ-s18Xg_xpCZHjy9mdrJbxkf8P448_bnCxNuOdPaOI9BKp1frhHplugk/pub?output=csv'
dfTitles = pandas.read_csv(strURL)
dfTitles = dfTitles.fillna('')

# Select only those titles marked for upload, which have rights information present
dfTitlesUpload = dfTitles
dfTitlesUpload = dfTitlesUpload.loc[dfTitlesUpload['Upload'] == 1]
dfTitlesUpload = dfTitlesUpload.loc[dfTitlesUpload['Rights information'] != '']
#dfTitlesUpload = dfTitlesUpload.loc[dfTitlesUpload['FDA Handle'] == '']
dfTitlesUpload = dfTitlesUpload.sort_values(['Filename'])

#%% Make sure files are actually present

vFiles = dfTitlesUpload['Filename'].tolist()
for strFile in vFiles:
	try:
		f = open('pdf_in/' + strFile)
	except:
		raise Warning('%s not found in folder. Verify that all files in the metadata table are present and retry.' % strFile)
		
#%% Generate thumbnails

for strPDF in vFiles:
	
	# Generate thumbnail file name
	strThumb = ThumbFileName(strPDF)
	
#	imgCover = convert_from_path('./pdf_in/' + strPDF, first_page=0, last_page=1)
#	imgCover = imgCover[0]
#	imgCover.resize([int(x*(600/max(imgCover.size))) for x in imgCover.size])
#	imgCover.save('./pdf_out/' + ThumbFileName(strPDF))
	
	# Create convert command
	strCmd = '/usr/local/bin/convert -thumbnail x600 -background white -alpha remove "./pdf_in/%s[0]" "./pdf_out/%s"' % (strPDF, strThumb)
	# Deal with the need to escape brackets in zsh
	strShell = os.environ['SHELL']
	if strShell.find('zsh') >= 0:
		strCmd = 'convert -thumbnail x600 -background white -alpha remove "./pdf_in/%s\[0\]" "./pdf_out/%s"' % (strPDF, strThumb)
	
	# Run thumbnail conversion
	iReturnCode = os.system(strCmd)
	if iReturnCode:
		raise Warning('''A required command (`convert`) was not found when running the script.
																Install ImageMagick and retry.''')
		
	
#%% Generate coverpages

# Get coverpage TeX template
with open('./coverpage/dscc_coverpage.tex', 'r') as f:
	strTeX = f.read()
	f.close()

# Loop through PDFs, create coverpage TeX, compile, move to pdf_out
for strPDF in vFiles:
	dfPDF = dfTitlesUpload.loc[dfTitlesUpload['Filename'] == strPDF]
	
	strAuthorLat = CleanCellString(dfPDF['Author (romanized or Latin-script original)'].iloc[0])
	strAuthorOrg = CleanCellString(dfPDF['Author (Original Script)'].iloc[0])
	strAuthor = CombineLatOrg(strAuthorLat, strAuthorOrg) 
	
	strTitleLat = CleanCellString(dfPDF['Title (Latin original or Romanized)'].iloc[0])
	strTitleOrg = CleanCellString(dfPDF['Title (original script)'].iloc[0])
	strTitle = CombineLatOrg(strTitleLat, strTitleOrg)
	
	# Fill template
	strPDFTeX = strTeX
	strPDFTeX = strPDFTeX.replace('{AUTHOR}', strAuthor)
	strPDFTeX = strPDFTeX.replace('{TITLE}', strTitle)
#	strPDFTeX = strPDFTeX.replace('{PDFFILENAME}', '../pdf_in/' + strPDF)
	
	strTeXFilename = re.sub(r'\.pdf$', '.tex', strPDF)
	f = open('./tex_out/' + strTeXFilename, 'w')
	f.write(strPDFTeX)
	f.close()
	
	# Run TeX compiler and deal with any errors
	strCmd = 'cd tex_out; xelatex %s; cd ..' % strTeXFilename
	iReturnCode = os.system(strCmd)
	if iReturnCode:
		raise Warning('''A required command (`xelatex`) was not found when running the script.
																Install a TeX distribution and retry.''')
	
	vPDFs = ['./tex_out/' + strPDF, './pdf_in/' + strPDF]
	merger = PdfFileMerger()
	for strPDFpart in vPDFs:
		merger.append(strPDFpart)
	
	merger.write('./pdf_out/' + strPDF)
	merger.close()

#%% Rearrange dataframe for FDA upload

dfFDA = dfTitlesUpload.loc[:, dfTitles.iloc[0] != '']
vFDAHandles = list(dfTitles.loc[0, dfTitles.iloc[0] != ''])
# Remove dc. from handles
vFDAHandles = [re.sub(r'^dc\.', '', s) for s in vFDAHandles]

# Drop the FDA Handle column, presumably the FDA Handle doesn't exist yet
dfFDA = dfFDA.drop(columns=['FDA Handle'])
vFDAHandles = vFDAHandles[1:]

# Sort by file name again for good measure
dfFDA = dfFDA.sort_values(['Filename'])

# Rename columns to Dublin Core names
dNewColumns = dict(zip(list(dfFDA.columns), vFDAHandles))
dfFDA = dfFDA.rename(columns=dNewColumns)

# Split out filename column so that it won't be added to the XML
dfFDAFiles = dfFDA['filename']
dfFDA = dfFDA.drop(columns=['filename'])


#%% Loop through files, create SAF for each file and create folders

# Delete the old archive and replace with new
if os.path.exists('./SimpleArchiveFormat'):
	shutil.rmtree('./SimpleArchiveFormat')
os.mkdir('SimpleArchiveFormat')

for i, strFile in enumerate(vFiles):
	
	strDir = 'item_%i' % (i + 1)
	
	# Make item directory and copy files into it
	os.mkdir('SimpleArchiveFormat/' + strDir)
	shutil.copyfile('./pdf_out/' + strFile, './SimpleArchiveFormat/' + strDir + '/' + strFile)
	shutil.copyfile('./pdf_out/' + ThumbFileName(strFile), './SimpleArchiveFormat/' + strDir + '/' + ThumbFileName(strFile))
	
	# Create contents file
	strContents = '%s\n%s' % (strFile, ThumbFileName(strFile))
	with open('SimpleArchiveFormat/' + strDir + '/contents', 'w') as f:
		f.write(strContents)
		f.close()
		
	# Create dublin_core.xml
	dfFile = dfFDA.loc[dfFDAFiles == strFile]
	strXML = GenerateDublinCoreXML(dfFile)
	with open('SimpleArchiveFormat/' + strDir + '/dublin_core.xml', 'w') as f:
		f.write(strXML)
		f.close()
		
	# Use the 'FDA Handle' column to store the item string for future reference
	# The mapfile produced by the FDA import provides only item string, not the PDF file name
	# Keeping the item string in the data alongside the PDF file name 
	# allows for the link between PDF, item, and FDA handle to remain constant
	dfTitles.loc[dfTitles['Filename'] == strFile, 'FDA Item'] = strDir


# Save the upload data for use in Step 2
# It needs to be saved to fix the data in the FDA upload so that everything lines up properly
# The Google Sheet may change at any time, 
# but none of those changes will be included from here forward
dfTitles.to_csv('FDA_upload.csv', index=False)

#%% Zip up new SAF
os.system('zip -r SimpleArchiveFormat.zip SimpleArchiveFormat')

# Delete files from zip, which will break uploader if present
os.system('zip -d SimpleArchiveFormat.zip __MACOSX/\*')
os.system('zip -d SimpleArchiveFormat.zip \*/.DS_Store')

#%% Delete all temporary files
# Disable this until everything is working really awesomely

if os.path.exists('./pdf_out'):
	shutil.rmtree('./pdf_out')
if os.path.exists('./tex_out'):
	shutil.rmtree('./tex_out')
if os.path.exists('./SimpleArchiveFormat'):
	shutil.rmtree('./SimpleArchiveFormat')














