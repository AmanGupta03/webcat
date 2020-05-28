""" consist routines to fetch data from siteinfo, sitedata table in web.db """

from collections import Counter
from tldextract import extract
from webdata import *
from math import ceil
import numpy as np 
import sqlite3 


def site_info_by_cluster(cluster_no=-1, limit=None):
  
  """ yield list [url, embeddings, cluster, rank] for url belong to *cluster_no*
      or of every cluster if *cluster_no* = -1.  
      
      Note-: support cluster_no as list of integers, in this case it yield info for all 
      cluster belongs to that list 
      
  """ 
  try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    #make query string
    query = 'SELECT *  FROM siteinfo'
    
    if(type(cluster_no) == int and cluster_no != -1): 
      query += ' WHERE cluster = ' + str(cluster_no)
    
    if(type(cluster_no) == list):
      query += ' WHERE cluster IN (' + ', '.join([str(i) for i in cluster_no]) + ')'

    
    if limit is not None: query += ' LIMIT ' + str(limit)

    rows = cur.execute(query)

    for row in rows:
      yield (row[0], np.frombuffer(row[1], dtype=float), row[2], row[3])
  
  except sqlite3.Error as error:
    print('error fetching data from site_info', error)


def site_info_by_key(key):
  """ return tuple (key, embedding in bytes, cluster, rank) from siteinfo 
      *key* is url as entered in database """
  
  try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    return cur.execute('SELECT * FROM siteinfo WHERE url=?', (key,)).fetchone()

  except sqlite3.Error as error:
    print('error fetching data from site_info', error)


def site_info_by_url(url):
  """ return tuple (url as entered in db, embedding as numpy array, cluster, rank) from siteinfo 
      *url* can be with or without prototype """
  
  url = extract(url).domain + '.' + extract(url).suffix
  row = site_info_by_key('https://'+url)

  if row is not None:
    return (row[0], np.frombuffer(row[1]), row[2], row[3] if row[3] != -1 else DB_DEFAULT_RANK)
  
  row = site_info_by_key('http://'+url)
  
  if row is not None:
    return (row[0], np.frombuffer(row[1]), row[2], row[3] if row[3] != -1 else DB_DEFAULT_RANK)


def site_keywords(url):
  """ return dictionary consist mapping of keywords and frequency of *url* 
      *url* shourld be in database """
  try:
    conn = sqlite3.connect(DB_PATH) 
    cur = conn.cursor()
    row = cur.execute('SELECT content FROM sitedata WHERE url = ?', (url,)).fetchone()

    return { w.split(':')[0] : int(w.split(':')[1]) for w in row[0].split()}

  except sqlite3.Error as error:
    print('error fetching data from sitedata', error)


def top_keywords(urls, count=10):
  """ return top *count* keywords from list of url *urls* 
      Note-: method is not optimised, to use only for small_list i.e upto size 100 """
  try:
    res = Counter()
    for url in urls:
      res += Counter(site_keywords(url))
    return [w[0] for w in res.most_common(count)]
  except:
    print('Error finding top keywords')

def get_cluster_websites(page=0, cluster_no=-1, limit=10):
  """ return dictionary consist *sites* i.e list of dictionary with fields (url, rank, change, approx) from globaldata of *cluster*
      and  *max_page*   
      Note -:  pages should be 0 to max_page-1 """
  
  try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    query = 'SELECT COUNT(*) FROM siteinfo'
    if cluster_no != -1: query += ' WHERE cluster = ' + str(cluster_no)
    
    max_page = ceil((cur.execute(query).fetchone()[0])/limit)
    
    if page >= max_page:
      return 'page not exist'

    #make query string
    offset = page*limit
    query = 'SELECT siteinfo.url, rank, rank_d29,cluster from siteinfo INNER JOIN sitedata on siteinfo.url = sitedata.url'
    if cluster_no != -1: query += ' WHERE cluster = ' + str(cluster_no)
    query += ' LIMIT ' + str(offset) + ',' + str(limit)

    #compute rank change
    change = lambda x, y: (x if x != -1 else DB_DEFAULT_RANK) - (y if y != -1 else DB_DEFAULT_RANK)

    #adjust rank 
    rank = lambda x: (x if x != -1 else DB_DEFAULT_RANK)

    #check whether change is approximate or not
    approx = lambda x, y: 1 if (x == -1 or y == -1) else 0

    get_info = lambda x: {'url': x[0], 'rank': rank(x[1]), 'change': change(x[1], x[2]), 'approx': approx(x[1], x[2]),'cluster': x[3]} 
    sites =  [get_info(x) for x in cur.execute(query).fetchall()]
    return {'sites': sites, 'max_page':max_page}

  except sqlite3.Error as error:
    print('error fetching cluster websites', error)
    return {}
