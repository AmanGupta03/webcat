""" 

Note-: Changing setings can cause inconsistency in globaldata as well as trends related data  

"""

__all__ = ['DB_PATH', 'DB_DATE', 'DB_DEFAULT_RANK', 'WINDOW', 'DB_FIRST_DATE', 'MAX_CLUSTER', 'MAX_WORDS']

import sqlite3

DB_PATH = './database/web.db'
KMEANS_PATH = './dump_obj/kmeans'
CLUSTERNAME_DB = './database/tempclustername.db'
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

#maximum no. of words per site to be kept in database
MAX_WORDS = 50

CRON_SETTINGS = {

  'SUFFICIENT': 50,   #Site will be rejected if scrapper found less than $SUFFICIENT words in it
  'TIMEOUT_SCRAPPER': 30, #max time in second scrapper wait for one url
  'TIMEOUT_STATUS_CHECK': 10, #max time in second status checker wait for one url
  'MAX_WAIT_FOR_RESPONSE': 5, #url will be rejected if it send nothing for this much seconds
  'LIMIT': 150000, # First $LIMIT entries will be consider from filtered cisco-ranklist
  'TEMP_DB_PATH': './database/temp.db',  #to use only during cron-job
  'WORKERS': 50,  #no of workers in multiprocessing
  'BATCH_SIZE': 200,  #no of urls attempt in one go.
  'BLACKLIST_TIME':4 #no of days a url will go in blacklist if it doesn't respond

}
