""" consist methods to update sitedata, siteinfo """

from crontools.newdomains import temp_read
from datetime import date, timedelta
from settings import DB_PATH, WINDOW
from tqdm import tqdm
import numpy as np
import sqlite3


def add_new_records(cur_date):
  """ Append new records in global_data """

  print('Adding new records...')  
  try:
    conn = sqlite3.connect(DB_PATH) 
    cur = conn.cursor()

    col = ['url', 'date', 'content']
    for r in range(30):
      col.append('rank_d'+str(r+1))

    ques = []
    for r in range(33):
      ques.append('?')

    query = 'INSERT INTO sitedata (' + ', '.join(col) + ') VALUES (' + ', '.join(ques) + ')'

    for row in tqdm(temp_read()):
      values = [row[0], str(cur_date), row[2]]
      values.extend([-1]*30)
      cur.execute(query, tuple(values))
      cur.execute('INSERT INTO siteinfo (url, embedding, cluster, rank) VALUES (?,?,?,?)', (row[0], row[1], -1, -1))
    conn.commit()
    
    print("Successfully added new records")
  except sqlite3.Error as error:
    print("Error while adding new records ", error)
  finally:
    if (conn): conn.close()


def delete_records(cur_date):
  """ Delete all records that doesn't enter in ranklist for given duration """

  expired = str(cur_date-timedelta(days=WINDOW))
  print('Deleting records prior to', expired, '...')
  try:
    conn = sqlite3.connect(DB_PATH) 
    cur = conn.cursor()
    cur.execute("SELECT url FROM sitedata WHERE date = ?", (expired,))
    urls = [row[0] for row in cur.fetchall()]
    cur.execute("DELETE FROM sitedata WHERE date = ?", (expired,))
    conn.commit()
    for url in tqdm(urls):
      cur.execute('DELETE FROM siteinfo where url=?', (url, ))
    conn.commit()
    print("Successfully removed", len(urls), 'entry')
  except sqlite3.Error as error:
    print("Error while deleting records", error)
  finally:
    if (conn): conn.close()


def update_rank(ranks):
  """ update rank_d1 to rank_d30 in sitedata and rank in siteinfo """

  print('updating ranks in globaldata...')
  query = "UPDATE sitedata SET "
  for i in range(1, 30):
    query += "rank_d" + str(i) + " = " + "rank_d" + str(i+1)
    if i != 29: query += ", "

  try:
    conn = sqlite3.connect(DB_PATH) 
    cur = conn.cursor()
    cur.execute(query)
    cur.execute('UPDATE sitedata SET rank_d30=-1')
    cur.execute('UPDATE siteinfo SET rank=-1')

    for row in tqdm(ranks):
      cur.execute('UPDATE sitedata SET rank_d30=? WHERE url=?', (row[1], row[0]))
      cur.execute('UPDATE siteinfo SET rank=? WHERE url=?', (row[1], row[0]))
    
    print("Successfully update ranks")
    conn.commit()
  except sqlite3.Error as error:
    print(error)
  finally:
    if (conn): conn.close()


def update_cluster(clusters):
  """ update cluster no of new_domains in global_data """
  print('updating cluster info...')
  try:
    conn = sqlite3.connect(DB_PATH) 
    cur = conn.cursor()
    
    for row in tqdm(clusters):
      cur.execute('UPDATE siteinfo SET cluster=? WHERE url=?', (int(row[1]), row[0]))

    conn.commit()
    print("Successfully update cluster no.")

  except sqlite3.Error as error:
    print(error)
  finally:
    if (conn): conn.close()


def update_date(urls, cur_date):
  """ update date of all domains global_data"""
  print('updating date...')
  try:
    conn = sqlite3.connect(DB_PATH) 
    cur = conn.cursor()
    
    for url in tqdm(urls):
      cur.execute('UPDATE sitedata SET date=? WHERE url=?', (cur_date, url))

    conn.commit()
    print("Successfully update date")

  except sqlite3.Error as error:
    print(error)
  finally:
    if (conn): conn.close()


def get_rank_cluster():
  """ return cluster and rank of all urls in siteinfo """
  try:
    conn = sqlite3.connect(DB_PATH) 
    cur = conn.cursor()
    cur.execute("SELECT cluster,rank FROM siteinfo")
    return cur.fetchall();

  except sqlite3.Error as error:
    print(error)

  finally:
    if (conn): conn.close()


def get_keyword_dict(url):
    """ return dictionary of keywords of url """
    try:
      conn = sqlite3.connect(DB_PATH) 
      cur = conn.cursor()
      row = cur.execute('SELECT content from sitedata where url=?', (url,)).fetchone()
      return { w.split(':')[0] : int(w.split(':')[1]) for w in row[0].split()}

    except sqlite3.Error as error:
      print(error)
    
    finally:
      if (conn): conn.close()


def get_all_vectors(cluster):
  """ return  dictionary consist list of urls, and embeddings of given cluster, 
      in case of None it return vectors of all cluster """


  try:    
    conn = sqlite3.connect(DB_PATH) 
    cur = conn.cursor()
    cursor = cur.execute('select url, embedding from siteinfo where cluster=?', (cluster,))

    urls, embedding = [], []
    
    for row in cursor:
      urls.append(row[0])
      embedding.append(np.frombuffer(row[1]))
    
    return dict({'embedding':embedding,'urls':urls})

  except sqlite3.Error as error:
    print(error)

  finally:
    if (conn): conn.close()