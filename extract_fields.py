# -*- coding: UTF-8 -*-

"""
"""

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# Imports
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import os
import re

from bs4 import BeautifulSoup
import pandas as pd

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# Constants
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

INPUT_DIR = 'downloaded_pages'

TAG_PATTERN = r'^(.*)\ \((.*)\)$'
GENDER_PATTERN = r'^Gender:\ (.*)$'
AGE_PATTERN = r'^Age\ at\ time\ of\ experience:\ (.*)$'
VIEWS_PATTERN = r'^(.*)Views:\ (.*)$'

COLUMN_NAMES = {
  0 : 'time',
  1 : 'dose',
  2 : 'method',
  3 : 'drug',
  4 : 'form' }

BLACKLIST = [
  '76264.html',
  '104064.html',
  '107837.html',
  '113853.html',
  '96749.html',
  '97965.html',
  '100398.html',
  '101638.html',
  '103561.html',
  '104633.html',
  '105583.html',
  '105583.html',
  '10622.html',
  '10624.html',
  '10626.html',
  '107096.html',
  '107242.html',
  '107245.html',
  '107777.html',
  '107789.html',
  '107891.html',
  '10884.html',
  '109350.html',
  '109355.html',
  '110580.html',
  '111217.html',
  '111219.html',
  '113613.html',
  '12474.html',
  '13248.html',
  '1947.html',
  '1949.html',
  '2213.html',
  '2244.html',
  '25288.html',
  '28355.html',
  '34560.html',
  '37622.html',
  '38705.html',
  '39914.html',
  '4933.html',
  '53142.html',
  '5866.html',
  '60495.html',
  '61222.html',
  '65963.html',
  '7779.html',
  '79599.html',
  '79605.html',
  '79606.html',
  '83181.html',
  '85686.html',
  '89668.html',
  '92208.html',
  '94415.html',
  '94457.html',
  '9469.html',
  '94991.html',
  '97433.html',
  '9808.html',
  '9895.html',
  '9897.html',
  '9913.html',
  '9916.html',
  '99161.html' ]

BAD_START = """<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">\n<html><head>\n<title>403 Forbidden</title>\n</head><body>\n<h1>Forbidden</h1>\n<p>You don\'t have permission to access /experiences/exp.php\non this server.<br />\n</p>\n<p>Additionally, a 403 Forbidden\nerror was encountered while trying to use an ErrorDocument to handle the request.</p>\n<hr>\n<address>Apache Server at www.erowid.org Port 443</address>\n</body></html>\n"""

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# Functions
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_tags( report ):

  footer = report.find_all( 'table' )[ -1 ]

  tags = footer.find_all( 'tr' )[-1].text
  tags = re.sub( r'\((.*?)\)', '', tags )
  tags = tags.replace( ':', ',')
  tags = tags.split( ',')
  tags = [ tag.strip( ) for tag in tags ]
  tags = ','.join( tags )

  return tags

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_weight( report ):

  try:
    stats = report.find( 'table', { 'class' : 'bodyweight' } )
    return stats.find( 'td', { 'class' : 'bodyweight-amount'} ).text
  except:
    return None

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_table( report ):

  table = report.find( 'table', { 'class' : 'dosechart'} )

  if table is not None:

    df = pd.read_html( str( table ).replace( 'DOSE:', '' ) )[ 0 ]
    df = df.rename( columns = COLUMN_NAMES )

    return df

  else:

    return None

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_text( report ):

  [ report.decompose( ) for report in report.find_all( 'table' ) ]

  return report.text.strip( '\n' )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_gender( report ):

  footer = report.find( 'table', { 'class' : 'footdata' } )

  text = footer.find_all( 'tr' )[ 1 ].text
  text = text.replace( '\xa0', '')
  gender = re.search( GENDER_PATTERN, text ).groups( )[ 0 ]

  return gender

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_age( report ):

  footer = report.find( 'table', { 'class' : 'footdata' } )

  text = footer.find_all( 'tr' )[ 2 ].text
  text = text.replace( '\xa0', '')
  age = re.search( AGE_PATTERN, text ).groups( )[ 0 ]

  return age

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_views( report ):

  footer = report.find( 'table', { 'class' : 'footdata' } )

  text = footer.find_all( 'tr' )[ 3 ].text
  text = text.replace( '\xa0', '')
  views = re.search( VIEWS_PATTERN, text ).groups( )[ 1 ]

  return views

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_report( report ):

  table = get_table( report )

  d = {
    'tags' : get_tags( report ),
    'weight' : get_weight( report ),
    'gender' : get_gender( report ),
    'age' : get_age( report ),
    'views' : get_views( report ),
    'text' : get_text( report ) }

  return d, table

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# Main
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

if __name__ == '__main__':

  files = os.listdir( INPUT_DIR )
  files = [ file for file in files if file not in BLACKLIST ]

  l = [ ]
  dfl = [ ]

  #---------------------------------------------------------------------------#

  for i, file in enumerate( sorted( files ) ):

    idx = file[ :-5 ]

    with open( os.path.join( INPUT_DIR, file ), 'r', encoding = "utf-8", errors="replace" ) as f:
      r = f.read( )

    if r.startswith( BAD_START ):
      r = r[ len( BAD_START ) : ]

    soup = BeautifulSoup( r, features = 'lxml' )
    report = soup.find_all( 'div', {'class' : 'report-text-surround'} )[ 0 ]
    report_data, table = get_report( report )

    if table is not None:
      table[ 'id' ] = idx
    report_data[ 'id' ] = idx

    l.append( report_data )
    dfl.append( table )

  #---------------------------------------------------------------------------#

  rdf = pd.DataFrame( l )
  tdf = pd.concat( dfl )

  rdf.to_csv( 'reports.csv', index = False )
  rdf.to_pickle( 'reports.df' )

  tdf.to_csv( 'dosage.csv', index = False )
  tdf.to_pickle( 'dosage.df' )

  #---------------------------------------------------------------------------#

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#