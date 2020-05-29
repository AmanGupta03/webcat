""" consist routines for search """

from webutils.processdata import average_word_embedding
from webdata.globaldata import site_info_by_cluster
from urllib.parse import urlparse
from numpy.linalg import norm
from webutils import dictionary
from textblob import TextBlob
from webtools import *
import sqlite3
from settings import CLUSTERNAME_DB

def autocorrect(words):
  """ autocorrect list of words if they are not in dictionary """
  res = []
  for word in words:
    if word not in dictionary: res.append(str(TextBlob(word).correct()))
    else: res.append(word)
  return res


def search_by_query(query, cluster=-1, result=20, limit=100000): 
  """ return *result* site based on search query from *cluster*, sorted according to rank  """ 
  
  query = autocorrect(query) 
  embd = average_word_embedding(query)
  sites = sorted([(norm(row[1]-embd), row[0], row[3] if row[3] != -1 else DB_DEFAULT_RANK) for row in site_info_by_cluster(cluster, limit=limit)], key=lambda x: x[0])
  return sorted([{'url': v[1], 'rank': v[2]} for v in sites[:result]], key=lambda x: x['rank'])


def search_by_domain(query, cluster=-1, results=50, limit=100000):
  """ return *result* site based on search domain from *cluster*, sorted according to rank  """ 

  domains = []
  for row in site_info_by_cluster(cluster, limit=limit):
    name = urlparse(row[0]).netloc
    for word in query:
      if word in name:
        domains.append({'url':row[0], 'rank':row[3] if row[3] !=- 1 else DB_DEFAULT_RANK})
  domains.sort(key=lambda x: x['rank'])
  return domains[0:results]


def update_cluster_name(cluster,name):
  try:
        conn = sqlite3.connect(CLUSTERNAME_DB) 
        cur = conn.cursor()
        cur.execute("UPDATE cluster_name set name=? where cluster=?",(name,cluster))
        conn.commit()
        conn.close()
  except:
        print("Error in connecting to database")
