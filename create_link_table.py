# -*- coding: UTF-8 -*-

"""Create database containing information about all Erowid experience reports
"""

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# Imports
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import requests
import re

import pandas as pd
from bs4 import BeautifulSoup
import numpy as np

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# Constants
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

URL = 'https://www.erowid.org/experiences/exp.cgi?ShowViews=0&Cellar=0&Start=0&Max=35000'

PATTERN = r'^(.*)\ \((.*)\)$'

LINK_PATTERN = r'^exp.php\?ID=(.*)$'

RATING_DICT = {
  None : None,
  'images/exp_new.gif' : 'new',
  'images/exp_star_1.gif' : '1',
  'images/exp_star_2.gif' : '2',
  'images/exp_star_3.gif' : '3' }

OUTPUT_HTML_FILE = 'erowid_page.html'

OUTPUT_HTML_TABLE_FILE = 'erowid_table.html'

OUTPUT_PANDAS_FILE = 'erowid_table.df'

OUTPUT_CSV_FILE = 'erowid_table.csv'


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# Functions that extract fields from the HTML table
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_rating( row ):

  rating = row.find_all( 'td' )[ 0 ]

  img = rating.find( 'img' )

  if img is None:
    return RATING_DICT.get( img )
  else:
    return RATING_DICT.get( rating.find( 'img' )[ 'src' ] )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_id( row ):

  link = row.find_all( 'td' )[ 1 ]
  link = link.find( 'a' )[ 'href' ]

  result = re.search( LINK_PATTERN, link ).groups( )[ 0 ]

  return int( result )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_title( row ):

  title = row.find_all( 'td' )[ 1 ]

  return title.text

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_username( row ):

  user = row.find_all( 'td' )[ 2 ]

  return user.text

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_drugs( row ):

  drugs = row.find_all( 'td' )[ 3 ].text
  drugs = drugs.replace( '&', ',')
  drugs = drugs.split( ',' )
  drugs = [ drug.strip( ) for drug in drugs ]
  drugs = ','.join( drugs )

  return drugs

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_date( row ):

  date = row.find_all( 'td' )[ 4 ]

  return date.text

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_row( row ):

  d = {
    'id' : get_id( row ),
    'rating' : get_rating( row ),
    'title' : get_title( row ),
    'username' : get_username( row ),
    'drugs' : get_drugs( row ),
    'date' : get_date( row ) }

  return d

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# Main
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

if __name__ == '__main__':

  # make GET request from HTML and parse using BeautifulSoup
  #---------------------------------------------------------------------------#

  # make GET request
  r = requests.get( URL )

  # parse response using BeautifulSoup and the `lxml` parser
  soup = BeautifulSoup( r.content, features = 'lxml' )

  # prepare HTML for consumption by extracting the longest table and removing
  # all other tables
  #---------------------------------------------------------------------------#

  # finding the longest table
  tables = soup.find_all( 'table' )
  table = tables[ np.argmax( [ len( table ) for table in tables ] ) ]

  # extract column names from HTML
  columns = table.find( 'tr' ).find_all( 'th' )
  columns = [ column.find( 'input' )[ 'value' ] for column in columns ]
  columns = [ column.lower( ) for column in columns ]

  # remove first row from table because it's not an experience entry
  table.find( 'tr' ).decompose( )

  # create list of rows from table, starting with the second one
  rows = table.find_all( 'tr' )[ 1 : ]

  # Populate fields and create DataFrame
  #---------------------------------------------------------------------------#

  # initialize empty list to store dicts of row data
  l = [ ]

  # loop over all rows in the table
  for row in rows:

    # append dict of row information to the list
    l.append( get_row( row ) )

  # create pandas DataFrame from list of dicts
  df = pd.DataFrame( l )

  #---------------------------------------------------------------------------#

  # write HTML response to file
  with open( OUTPUT_HTML_FILE, 'w' ) as f:
    f.write( r.text )

  # write pickled pandas DataFrame to file
  df.to_pickle( OUTPUT_PANDAS_FILE )

  # write pandas DataFrame to csv file
  df.to_pickle( OUTPUT_CSV_FILE )

  # write HTML table to file
  with open( OUTPUT_HTML_TABLE_FILE, 'w' ) as f:
    f.write( str( table ) )

  #---------------------------------------------------------------------------#

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#