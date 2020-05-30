from datetime import date, timedelta
from settings import CRON_SETTINGS
from crontools import newdomains
from crontools import globaldata
from crontools import trends
from settings import *
import numpy as np
import sys
import os

LIMIT = CRON_SETTINGS['LIMIT']

def getting_update(cur_date, workers, batch_size):
  """ it will fetch and scrap all the updates for current date """

  print('Updating Database Using Cisco Ranklist Of', cur_date, '...\n')
  
  print('Fetching cisco ranklist...')
  urls = newdomains.fetch_ranklist(cur_date)
  
  print('Filtering cisco ranklist...')
  urls = newdomains.process_ranklist(urls)[:LIMIT]

  print('Filtering Already visited domains...')
  url_to_scrap = newdomains.get_url_to_scrap(urls)
  print('\n',len(url_to_scrap), 'new domains found')
  
  print('\nScrapping urls...')
  newdomains.fast_scrap_batches(url_to_scrap, workers, batch_size)

  return urls, url_to_scrap


def update(cur_date, urls, url_to_scrap):
  """ this will update kmeans, and web.db """

  new_urls = []
  embedding = []

  for data in newdomains.temp_read():
    new_urls.append(data[0])
    embedding.append(np.frombuffer(data[1]))

  print('\n',len(new_urls), 'new domains scrapped')

  rejected = newdomains.get_reject_list(url_to_scrap, new_urls)

  print('\nAdjusting ranks...')
  ranks = newdomains.get_adjusted_ranks(cur_date, new_urls, urls)

  print('performing updates on global_data.....')

  globaldata.add_new_records(cur_date)
  globaldata.delete_records(cur_date) 
  globaldata.update_rank(list(ranks.items()))
  globaldata.update_date(list(ranks.keys()), str(cur_date))

  print('updating trends.......')
  trends.update_trends(new_urls, embedding, str(cur_date))

  print('updating visited domains...')
  newdomains.update_visited_domains(list(ranks.keys()), new_urls, cur_date)
  newdomains.add_new_visited_domains(rejected, cur_date, status=0)
  newdomains.delete_blacklisted(cur_date)

  print('clearing temporary data...')
  newdomains.temp_clear()

  print('SUCCESS\n')


def run(workers=None, batch_size=None):
  """ run pending updates """

  if(workers is None): workers = CRON_SETTINGS['WORKERS']
  if(batch_size is None): batch_size = CRON_SETTINGS['BATCH_SIZE']

  print('\nWARNING-: Scrapper will use ', workers, 'parallel workers and batch size', batch_size, '\n')

  str_to_date = lambda s: date(int(s[0:4]),int(s[5:7]),int(s[8:10]))
  cur_date = str_to_date(DB_DATE) + timedelta(days=1)
  till_date = date.today() - timedelta(days=1)

  print('Ready to perform all updates from', cur_date, 'to', till_date, '\n')
  
  while(cur_date <= till_date):
    try:
      newdomains.temp_clear()
      urls, url_to_scrap = getting_update(cur_date, workers, batch_size)
      #SHUT DOWN SERVER HERE.....
      os.system("./server_stop.sh")
      update(cur_date, urls, url_to_scrap)
      #RESTART SERVER HERE....
      os.system("./server_start.sh")
      cur_date += timedelta(days=1)
    except Exception as e:
      print('Error while updating at', cur_date, e)
      print('Stop updates')
      break
  
if len(sys.argv) == 1: run()
if len(sys.argv) == 2: run(int(sys.argv[1]))
if len(sys.argv) == 3: run(int(sys.argv[1]), int(sys.argv[2]))
