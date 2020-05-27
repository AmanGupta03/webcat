""" consist routines to processurl, ie finding similar sites, cluster, keywords etc """

from webutils.processdata import sent_embedding
from webutils.scrapper import get_text_content
from webdata import globaldata, trendsdata
from numpy.linalg import norm
from webtools import *
import traceback
import json

  
def get_similar_sites(embd, cluster=-1, top=10, improve=True, limit=11): 
  """ return *top* sites similar to site having embedding *embd* 
      if *improve* = True it will also look for *limit* neighbour of cluster 
      Note -:  Do not change default value of *limit* until necessary """

  if cluster != -1 and improve: 
    temp = list(neigh[cluster][:limit])
    temp.append(cluster)
    cluster = temp 

  sim = sorted([(norm(row[1]-embd), row[0]) for row in globaldata.site_info_by_cluster(cluster)], key=lambda x: x[0])
  return [v[1] for v in sim[:top]]


def fetch_url_info(url, lookup=True):
  """ return tuple (embeddings as numpy array, cluster, status) for url """
  
  try:
    url_info = None
    if lookup: url_info = globaldata.site_info_by_url(url)
    
    if url_info is not None:
      return (url_info[1], url_info[2], 'success')
    
    else:
      url_info = get_text_content(url)
      
      if url_info['status'] == 'fail':
        return (-1, -1, url_info['content'])
      else:
        embd = sent_embedding(url_info['content'])
        return (embd, kmeans.predict([embd])[0], url_info['status'])
  
  except Exception as e:
    print('fetch_url_info error', e)
    print(traceback.format_exc())
    return (-1, -1, 'failed due to some unknown reason')


def get_processed_info(url, near=True, comp_search=False, lookup=True, top=10, improve=True, limit=11):

  """ return dictionary with keys (keywords, similar_websites, cluster, status) for url
      if near is false, then similar_sites will not return, else *top* similar sites will 
      return. if *improve* = True it will also look for *limit* neighbour of cluster for finding 
      similar sites.

      Note-: it return cluster acc to 1 based indexing 
            Do not change default value of *limit* until necessary"""

  try:
    url_info = fetch_url_info(url, lookup)

    if url_info[1] == -1:
      return json.dumps({"keywords":[],"websites":[],"status":url_info[2]})
    
    keywords = trendsdata.keywords_by_cluster(url_info[1]).split()
    
    if near == False:
      return json.dumps({"keywords": keywords,"websites":[],'status':url_info[2],"cluster_no":str(url_info[1]+1)})
    
    similar_sites = []

    if comp_search: similar_sites = get_similar_sites(url_info[0])
    else: similar_sites = get_similar_sites(url_info[0], url_info[1], top, improve, limit)

    keywords = globaldata.top_keywords(similar_sites)
    
    return json.dumps({"keywords": keywords,"websites":similar_sites,'status':url_info[2],"cluster_no":str(url_info[1]+1)})
  
  except Exception as e:
    print('ERROR_MSG',e)
    return json.dumps({"keywords":[],"websites":[], "status": 'failed due to some unknown reason'})