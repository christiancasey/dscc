# DSCC Uploader

## Overview

The basic goal of this program is to add new texts to the DSCC collection. 
This comprises adding a new text to the [DSCC website](http://dcaa.hosting.nyu.edu/dscc/), 
	which includes both a description of the text 
	and a link to the PDF of the actual text itself.
The files containing the text are hosted on the [Faculty Digital Archive](https://archive.nyu.edu).
That is, the actual text is not in the Omeka-based [DSCC website](http://dcaa.hosting.nyu.edu/dscc/).
That website displays bibliographic data and a link to the text.

It is best to think of the DSCC project as existing in two major parts:
1. The public-facing list of texts, which is the [DSCC website](http://dcaa.hosting.nyu.edu/dscc/).
2. The backend file hosting, which is the [Faculty Digital Archive](https://archive.nyu.edu).



This set of scripts adds PDFs with metadata to the [Faculty Digital Archive](https://archive.nyu.edu) and links them to the [DSCC Webpage](http://dcaa.hosting.nyu.edu/dscc/).

It also performs a number of intermediate tasks, such as creating thumbnails and adding cover pages.



## Requirements

The scripts require third-party software to perform some essential tasks. 
Before running the scripts themselves, these programs must be installed on your system.
*NB These instructions are designed for OSX users. For all other operating systems, you will need to translate these steps into your system's equivalents.*

### ImageMagick

ImageMagick](https://imagemagick.org) produces the thumbnail images from the PDFs, and so must be installed in advance.
The easiest way to do this is to enter the following in terminal:
`brew install imagemagick`

This method requires [Homebrew](https://brew.sh), which can be installed from terminal using: `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

### TeX

Install the latest TeX distribution. For Mac users, this is [MacTeX](http://www.tug.org/mactex/mactex-download.html). Download the [package](http://tug.org/cgi-bin/mactex-download/MacTeX.pkg), run it, and follow the instructions. Keep the default installation folder, which should be: `/Library/TeX/texbin/`

## (Ideal) User Workflow

### Basic Outline

1. Create the archive for FDA
2. Choose the archive from the FDA website
3. Copy the output log from the FDA upload
4. Publish it all to the DSCC website

### Specific Instructions

1. Place all PDF files in the directory `./pdf_in`
	1. NB This should be handled by the program itself in future versions.
	2. Right now, the Box API is not working, so you have to place the files manually.
2. Run `Step 1 – Create FDA Upload`
	1. `python "Step 1 – Create FDA Upload.py"`
	2. This will create the file `SimpleArchiveFormat.zip`
3. In the [FDA Website](https://archive.nyu.edu/handle/2451/43776), select "Batch Upload" and choose `SimpleArchiveFormat.zip`
4. Highlight and copy the output log from the FDA upload
	1. NB The next script uses the data on the clipboard, so run it immediately after copying.
5. Run ``

## Program Workflow

1. Access metadata table
2. Download PDFs
3. Create thumbnails from first pages of PDFs
4. Add DSCC cover pages to PDFs
5. Upload new PDF and thumbnails to [FDA](https://archive.nyu.edu)
6. Acquire list of FDA URIs
7. Add new entries to Omeka site ([DSCC Webpage](http://dcaa.hosting.nyu.edu/dscc/))