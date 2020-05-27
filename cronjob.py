from datetime import date, timedelta
from settings import CRON_SETTINGS
from crontools import newdomains
from crontools import globaldata
from crontools import trends
from settings import *
import numpy as np


LIMIT = CRON_SETTINGS['LIMIT']


def getting_update(cur_date):
  """ it will fetch and scrap all the updates for current date """

  print('This will update database using cisco ranklist of', cur_date)
  
  print('Fetching cisco ranklist...')
  urls = newdomains.fetch_ranklist(cur_date)
  
  print('Filtering cisco ranklist...')
  urls = newdomains.process_ranklist(urls)[:LIMIT]

  print('Filtering Already visited domains...')
  url_to_scrap = newdomains.get_url_to_scrap(urls)
  print('\n',len(url_to_scrap), 'new domains found')
  
  print('\nScrapping urls...')
  newdomains.fast_scrap_batches(url_to_scrap)

  return urls


def update(cur_date, urls):
  """ this will update kmeans, and web.db """

  new_urls = []
  embedding = []

  for data in newdomains.temp_read():
    new_urls.append(data[0])
    embedding.append(np.frombuffer(data[1]))
  
  print('\n',len(new_urls), 'new domains scrapped')

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

  print('clearing temporary data...')
  newdomains.temp_clear()

  print('SUCCESS')


str_to_date = lambda s: date(int(s[0:4]),int(s[5:7]),int(s[8:10]))
cur_date = str_to_date(DB_DATE) + timedelta(days=1)

newdomains.temp_clear()

urls = getting_update(cur_date)
#SHUT DOWN SERVER HERE.....
update(cur_date, urls)