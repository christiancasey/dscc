#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 12:43:18 2019

@author: christiancasey

Create thumbnails from first page of PDFs. Update PDFs with coverpage.
"""


import os
import glob
import re
import pandas
import pygsheets
from PyPDF2 import PdfFileMerger

#%% Function definitions

# Eliminate junk before and after entries
def CleanCellString( strCell ):
	strCell = re.sub(r'^\W*', '', strCell)
	strCell = re.sub(r'\W*$', '', strCell)
	return strCell

# Combine both Latin and non-Latin data where available
def CombineLatOrg( strLat, strOrg ):
	strLat = strLat.strip()
	strOrg = strOrg.strip()
	
	if len(strLat) > 0 and len(strOrg) > 0:
		return strOrg + ' – ' + strLat
	
	return strOrg + strLat

#%% Prepare temporary directories for content

# Delete everything in the directory: pdf_out
vFiles = glob.glob('./pdf_out/*')
for strFile in vFiles:
	os.system('rm "%s"' % strFile)
	
# Delete everything in the directory: tex_out
vFiles = glob.glob('./tex_out/*')
for strFile in vFiles:
	os.system('rm "%s"' % strFile)

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
		
#%% Generate thumbnails

for strPDF in vFiles:
	
	# Generate thumbnail file name
	strThumb = re.sub(r'\.pdf$', '_thumb.png', strPDF)
	
	# Create convert command
	strCmd = 'convert -thumbnail x600 -background white -alpha remove "./pdf_in/%s"[0] "./pdf_out/%s"' % (strPDF, strThumb)
	# Deal with the need to escape brackets in zsh
	strShell = os.environ['SHELL']
	if strShell.find('zsh') >= 0:
		strCmd = 'convert -thumbnail x600 -background white -alpha remove "./pdf_in/%s"\[0\] "./pdf_out/%s"' % (strPDF, strThumb)
	
	# Run thumbnail conversion
	os.system(strCmd)

#%% Generate coverpages

# Get coverpage TeX template
with open('./coverpage/dscc_coverpage.tex', 'r') as f:
	strTeX = f.read()
	f.close()

# Loop through PDFs, create coverpage TeX, compile, move to pdf_out
for strPDF in vFiles:
	dfPDF = dfTitlesUpload.loc[ dfTitlesUpload['Filename'] == strPDF ]
	
	strAuthorLat = CleanCellString( dfPDF['Author (romanized or Latin-script original)'].iloc[0] )
	strAuthorOrg = CleanCellString( dfPDF['Author (Original Script)'].iloc[0] )
	strAuthor = CombineLatOrg( strAuthorLat, strAuthorOrg ) 
	
	strTitleLat = CleanCellString( dfPDF['Title (Latin original or Romanized)'].iloc[0] )
	strTitleOrg = CleanCellString( dfPDF['Title (original script)'].iloc[0] )
	strTitle = CombineLatOrg( strTitleLat, strTitleOrg )
	
	# Fill template
	strPDFTeX = strTeX
	strPDFTeX = strPDFTeX.replace('{AUTHOR}', strAuthor)
	strPDFTeX = strPDFTeX.replace('{TITLE}', strTitle)
#	strPDFTeX = strPDFTeX.replace('{PDFFILENAME}', '../pdf_in/' + strPDF)
	
	strTeXFilename = re.sub( r'\.pdf$', '.tex', strPDF )
	f = open( './tex_out/' + strTeXFilename, 'w' )
	f.write(strPDFTeX)
	f.close()
	
#	os.system('cd tex_out')
	os.system('cd tex_out; xelatex %s; cd ..' % strTeXFilename)
#	os.system('cd ..')
	
	vPDFs = [ './tex_out/' + strPDF, './pdf_in/' + strPDF ]
	merger = PdfFileMerger()
	for strPDFpart in vPDFs:
		merger.append(strPDFpart)
	
	merger.write( './pdf_out/' + strPDF )
	merger.close()

































