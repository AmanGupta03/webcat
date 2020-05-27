""" This scraper is designed only for cron job 
    use *webutils.scrapper* for processing client request 
"""

from webutils.processdata import sent_embedding_in_bytes, compress_sentence, preprocess
from crontools.timeout import Timeout
from settings import CRON_SETTINGS
from bs4 import BeautifulSoup
from bs4.element import Comment
from tldextract import extract
import requests
import warnings

warnings.filterwarnings("ignore")

headers = {
	'User-Agent': 'Mozilla/75.0',
	'Accept-Language': 'en-US,en;q=0.5'
}


SUFFICIENT = CRON_SETTINGS['SUFFICIENT']
T1 = CRON_SETTINGS['TIMEOUT_STATUS_CHECK']
T2 = CRON_SETTINGS['MAX_WAIT_FOR_RESPONSE']
T3 = CRON_SETTINGS['TIMEOUT_SCRAPPER']
DEFAULT_STATUS = 0 #in case of excetion this status will return 


def get_status_code(url):
  """ return status code of url and *DEFAULT_STATUS* in case of exception """
  try:
    with Timeout(T1):
      res = requests.get(url, headers=headers, verify=False, timeout=T2, stream=False, allow_redirects=True)
      return res.status_code
  except:
    return DEFAULT_STATUS
  return DEFAULT_STATUS


def get_valid_url(url):
  """ return url with valid protocol if they are active else None """

  if get_status_code('https://'+url) == 200:
    return 'https://'+url
  elif get_status_code('http://'+url) == 200:
    return 'http://'+url


def tag_visible(element):
  """ check visible tag """

  if element.parent.name in ['style', 'script', 'head', 'meta', '[document]']:
      return False
  if isinstance(element, Comment):
      return False
  return True


def text_from_html(html):
  """ Extract visible text from html body """

  soup = BeautifulSoup(html, 'html.parser')
  text = soup.findAll(text=True)
  visible_text = filter(tag_visible, text)  
  return u" ".join(t.strip() for t in visible_text)


def get_about_url(html, url):
  """  return url of about page if exist """
  try:
    domain = extract(url).domain.lower()  #fetch domain name of site
    soup = BeautifulSoup(html, 'html.parser')
  
    for link in soup.find_all('a'):
      if link.get('href') != None and 'about' in link.get('href').lower() and domain in link.get('href').lower():
        return link.get('href')
  except:
    return None


def get_static_text_content(url):
  """ scrap static content form url and preprocess it """

  content = []
  
  try:
    with Timeout(T3):
      res = requests.get(url, headers=headers, verify=False, timeout=T2, allow_redirects=True)
      content.extend(preprocess(text_from_html(res.text)))
      if len(content) > 0 and content[0] == "invalidcontentfound": return content

      abt_url = get_about_url(res.text, url)

      if abt_url != None:
        try:
          res = requests.get(abt_url, headers=headers, verify=False, timeout=T2, allow_redirects=True)
          content.extend(preprocess(text_from_html(res.text)))
        except:
          return content
      return content
    
  except:
    return content
  return content


def get_all_info(url):

  """ return tuple (url, embedding in bytes, compressed content) or None if either url has insufficient content
      or some error occur """

  url = get_valid_url(url)

  if url is None: 
    return None
  
  content = get_static_text_content(url)
  
  if len(content) < SUFFICIENT: 
    return None
  
  content = ' '.join(content) 

  return (url, sent_embedding_in_bytes(content), compress_sentence(content))