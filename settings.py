""" Every Package depends on this module
    do not modify it  """

__all__ = ['DB_PATH', 'DB_DATE', 'DB_DEFAULT_RANK', 'WINDOW', 'DB_FIRST_DATE', 'MAX_CLUSTER']

import sqlite3

DB_PATH = './database/web.db'

def get_last_update_date():
  """ return string consist date upto which database is updated """
  
  print('loading database updates...')
  
  try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    return cur.execute('SELECT date_p FROM size ORDER BY date_p DESC LIMIT 1').fetchone()[0]

  except sqlite3.Error as error:
    print('error finding present date', error)

#present date according to database
DB_DATE = get_last_update_date()

#default rank
DB_DEFAULT_RANK = 150000  

#sitedata consist only site that  found in last *WINDOW* days
WINDOW = 30

#no of clusters
MAX_CLUSTER = 100

#date at which project started
DB_FIRST_DATE = '2020-04-07'