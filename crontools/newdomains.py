""" consist routines to process new domains found in cisco ranklist """

from concurrent.futures import ProcessPoolExecutor, as_completed
from settings import CRON_SETTINGS, DB_PATH, WINDOW
from crontools.scrapper import get_all_info
from datetime import date, timedelta
from tldextract import extract
from math import ceil
from tqdm import tqdm
import pandas as pd
import sqlite3

CISCO_RANKLIST = 'http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m-{date:}.csv.zip'
TEMP_DB_PATH = CRON_SETTINGS['TEMP_DB_PATH']
WORKERS = CRON_SETTINGS['WORKERS']
BATCH_SIZE = CRON_SETTINGS['BATCH_SIZE']
BLACKLIST_TIME = CRON_SETTINGS['BLACKLIST_TIME']


def fetch_ranklist(date):
  """ fetch cisco ranklist of given date """

  df = pd.read_csv(CISCO_RANKLIST.format(date=date))
  urls = [row[1] for row in df.values.tolist()] 
  urls.insert(0, df.columns[1])
  return urls


def is_valid(url):
  """ return true if url is domain or false if it is subdomain """
  
  if not url.startswith('http'): 
    url = 'https://'+ url

  try:
    subdomain = extract(url).subdomain
    if subdomain == "" or subdomain == "www": return True
    else: return False
  except:
    return False


def process_ranklist(urls):
  """ remove subdomain/invalid domains and redundancy from list """
  
  valid_urls = list(filter(is_valid, urls))
  
  seen = set()
  res = []
  
  for url in tqdm(valid_urls):
    domain = extract(url).domain
    if domain not in seen:
      res.append(url)
      seen.add(domain)

  return res


def get_visited_domains():
  """ return set of visited domains fetched from database  """

  try:
    conn = sqlite3.connect(DB_PATH) 
    cur = conn.cursor()

    cur.execute('SELECT url FROM visited')
    return set([extract(data[0]).domain for data in cur.fetchall()])

  except sqlite3.Error as error:
    print(error)
  finally:
    if (conn): conn.close()


def get_all_fetched_domains(cur_date):
  """ return set of all domains that are also in globaldata """

  expired = str(cur_date-timedelta(days=WINDOW))
  try:
    conn = sqlite3.connect(DB_PATH) 
    cur = conn.cursor()
    cur.execute('SELECT url From visited WHERE status = 1 AND date != ?', (expired,))
    return [data[0] for data in cur.fetchall()]
  except sqlite3.Error as error:
    print(error)
  finally:
    if (conn): conn.close()


def get_url_to_scrap(urls):
  """ remove already visited domains and adjust format of urls """

  visited_domains = get_visited_domains()
  new_visited_domains = set()
  url_to_scrap = []

  for url in tqdm(urls):
    domain = extract(url).domain
    suffix = extract(url).suffix
    if domain not in visited_domains and domain not in new_visited_domains:
      new_visited_domains.add(domain)
      url_to_scrap.append(domain+'.'+suffix)
  
  return url_to_scrap


def get_reject_list(all_urls, scrapped_urls):
  """ return list of rejected urls """

  domains = set([extract(url).domain for url in scrapped_urls])
  return [url for url in all_urls if extract(url).domain not in domains]


def temp_insert(values):
  """ insert data in temporary databse """

  try:
    conn = sqlite3.connect(TEMP_DB_PATH)
    cur = conn.cursor()
    cur.execute('INSERT INTO temp (url, embedding, content) VALUES (?, ?, ?)', values)
    conn.commit() 
  except sqlite3.Error as error:
    print(error)
  finally:
    if (conn): conn.close()


def temp_read():
  """ yield tuple (url, embedding, keywords) from temporary database """

  try:
    conn = sqlite3.connect(TEMP_DB_PATH)
    cur = conn.cursor()
    rows = cur.execute('SELECT * FROM temp')
    for row in rows:
      yield row

  except sqlite3.Error as error:
    print(error)
  finally:
    if (conn): conn.close()


def temp_clear():
  """ remove all data from temporary database """

  try:
    conn = sqlite3.connect(TEMP_DB_PATH)
    cur = conn.cursor()
    cur.execute('DELETE FROM temp')
    conn.commit()
  except sqlite3.Error as error:
    print(error)
  finally:
    if (conn): conn.close()


def fast_scrap(urls, workers=WORKERS):
  """ Avoid dynamic content scrapping as webdriver cannot handle multiprocessing """

  with ProcessPoolExecutor(max_workers=workers) as executor:
    futures = [executor.submit(get_all_info, url) for url in urls]

    for result in as_completed(futures):
      if result.result() is not None:
        temp_insert(result.result())


def fast_scrap_batches(urls, workers=WORKERS, batch_size=BATCH_SIZE):
  """ 
    This will scrap only domains upto 'batch_size' in one go. 
    this is necessary to minimize loss during failure in fast_scrap
  """
  
  total_phase = ceil(len(urls)/batch_size)
  print('scrapping will be done in', total_phase, 'phase  where', batch_size, 'urls attempt in each phase')

  for i in tqdm(range(total_phase)):
    try:
      l = batch_size*i;
      r = batch_size*(i+1) 
      fast_scrap(urls[l:r])
    except:
      print('phase', i, 'failed')
      continue


def get_adjusted_ranks(cur_date, new_urls, urls):
  """ return current_day ranklist of all urls in data """

  all_fetched_urls = set(get_all_fetched_domains(cur_date))

  for url in new_urls:
    all_fetched_urls.add(url)
  
  present_domains = set()
  url_dict = {}
  
  # map domain name with their url 
  for url in tqdm(all_fetched_urls):
    domain = extract(url).domain
    present_domains.add(domain)
    url_dict[domain] = url

  # filter duplicates/inactive/unscrapped domains
  seen = set()
  adjusted_rank_list = []
  for url in tqdm(urls):
    domain = extract(url).domain
    if domain not in seen and domain in present_domains:
      adjusted_rank_list.append(url_dict[domain])
      seen.add(domain)

  ranks = {url:(i+1) for i,url in enumerate(adjusted_rank_list)}
  return ranks


def delete_blacklisted(cur_date):
  """ delete entries that are blacklisted for more than $BLACKLIST_TIME """

  expired = str(cur_date-timedelta(days=BLACKLIST_TIME))
  try:
    conn = sqlite3.connect(DB_PATH) 
    cur = conn.cursor()
    cur.execute("DELETE FROM visited WHERE status=0 and date = ?", (expired,))
    conn.commit()
  except sqlite3.Error as error:
    print(error)
  finally:
    if (conn): conn.close()



def delete_visited_domain(cur_date):
  """ delete all entries in visited_domains table that are 30days old """
  expired = str(cur_date-timedelta(days=WINDOW))
  try:
    conn = sqlite3.connect(DB_PATH) 
    cur = conn.cursor()
    cur.execute("DELETE FROM visited WHERE status=1 and date = ?", (expired,))
    conn.commit()
  except sqlite3.Error as error:
    print(error)
  finally:
    if (conn): conn.close()


def add_new_visited_domains(new_url, cur_date, status=1):
  """ Add new entries in visited table, that found at cur_date """

  row = [[url, str(cur_date), status] for url in new_url]
  df = pd.DataFrame(row, columns=['url', 'date', 'status'])
  df.set_index('url', inplace=True)

  try:
    conn = sqlite3.connect(DB_PATH) 
    df.to_sql('visited', conn, if_exists='append', index=True)
    conn.commit()
  except sqlite3.Error as error:
    print("Error while adding new records in visited", error)
  finally:
    if (conn): conn.close()
  

def update_visited_domains_date(urls, cur_date):
  """ update date column in visited table """
  
  try:
    conn = sqlite3.connect(DB_PATH) 
    cur = conn.cursor()

    for url in tqdm(urls):
      cur.execute('UPDATE visited SET date=? WHERE url=?', (cur_date, url))
    conn.commit()
  
  except sqlite3.Error as error:
    print(error)
  
  finally:
    if (conn): conn.close()
  


def update_visited_domains(all_url, new_url, cur_date):
  """ Add all url seen at cur_date and delete url that doesn't encounter in last x days """
  
  delete_visited_domain(cur_date)
  add_new_visited_domains(new_url, cur_date)
  update_visited_domains_date(all_url, str(cur_date))