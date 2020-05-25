""" Note -: This Module require chromium-chrome driver to work correctly
            Install using command "apt install chromium-chromedriver"

            consist routines for text scrapping from websites
"""


from bs4 import BeautifulSoup
from bs4.element import Comment
from tldextract import extract
from selenium import webdriver
from webutils import processdata
import requests
import warnings

warnings.filterwarnings("ignore")

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
browser = webdriver.Chrome('chromedriver',chrome_options=chrome_options)
browser.set_page_load_timeout(10)

headers = {
	'User-Agent': 'Mozilla/75.0',
	'Accept-Language': 'en-US,en;q=0.5'
}

SUFFICIENT = 50  #Minimum words require to avoid dynamic content scrapping
MINIMUM = 10 #Minimum content required


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


def get_static_text_content(url, timeout=5):
  """ scrap static content form url and preprocess it """

  content = []

  try:
    res = requests.get(url, headers=headers, verify=False, timeout=timeout, allow_redirects=True)
    res.raise_for_status()
    content.extend(processdata.preprocess(text_from_html(res.text)))
    if len(content) > 0 and content[0] == "invalidcontentfound": 
      return ['ERROR_MSG', 'Non English']
    abt_url = get_about_url(res.text, url)
    if abt_url != None:
      try:
        res = requests.get(abt_url, verify=False, timeout=timeout, allow_redirects=True)
        content.extend(processdata.preprocess(text_from_html(res.text)))
      except: return content
  
  except requests.exceptions.Timeout as errt:
    return ['ERROR_MSG', 'Timeout: (connect time={timeout:} sec)'.format(timeout=timeout)]
  except requests.exceptions.HTTPError as errh:
    return ['ERROR_MSG', str(errh.args[0])]
  except requests.exceptions.ConnectionError as errc:
    return ['ERROR_MSG', str(errc.args[0]).split(':')[-1]]
  except requests.exceptions.RequestException as err:
    return ['ERROR_MSG', str(err.args[0])]
  return content


def get_dynamic_text_content(url):
  """ scrap dynamic content form url and preprocess it """
  
  content = []
  try:
    browser.get(url)
    content.extend(processdata.preprocess(text_from_html(browser.page_source)))
    if len(content) > 0 and content[0] == "invalidcontentfound": 
      return ['ERROR_MSG', 'Non English']
    abt_url = get_about_url(browser.page_source, url)
   
    if abt_url != None:
      browser.get(abt_url)
      content.extend(processdata.preprocess(text_from_html(browser.page_source)))
    return content
  except:
    return ['ERROR_MSG', 'site take too long to complete request']


def get_scrapped_text(url, dynamic, timeout=5):
  """ scrap text content from url """

  content = get_static_text_content(url, timeout) 
  if len(content) > 0 and content[0] == 'ERROR_MSG': return content
  dy_content = []
  if (len(content) < SUFFICIENT and dynamic): dy_content = get_dynamic_text_content(url)
  if len(content) >= len(dy_content): return content
  else: return dy_content 


def get_url_and_content(url, dynamic=True, timeout=5):
  """ return dictionary object with url, and scrapped_content """

  final_url = url
  content = []
  
  if url.startswith('http'):
    content = get_scrapped_text(url, dynamic, timeout)
  else:
    content = get_scrapped_text('https://'+url, dynamic, timeout)
    final_url = 'https://'+url
    if len(content) < MINIMUM:
      content = get_scrapped_text('http://'+url, dynamic, timeout)
      final_url = 'http://'+url
  
  return {'url': final_url, 'content': content}


def get_text_content(url, dynamic=True, timeout=5, modify_url=True):
  """ params -: url -: as a string with or without http/https
                Note it will find suitable protocol b/w http and https automatically if doesn't include in url
                dynamic -: boolean variable to decide whether to scrap dynamic content or not

                return -: dictionary consist of 'status', 'content', 'url'
                          content will be error message if 'status' = fail """

  if(modify_url and (not url.startswith('http'))):
     url = extract(url).domain + '.' + extract(url).suffix
  data =  get_url_and_content(url, dynamic, timeout)
  content = data['content']
  if(modify_url): url = data['url']
  status = ''
  
  if len(content) > 0 and content[0] == 'ERROR_MSG': 
    status = 'fail'
    content = content[1]
  elif len(content) < MINIMUM:
    status = 'fail'
    content = 'Insufficient text content scrapped from site, cannot process request further'
  else:
    status = 'success'
    content = ' '.join(content)
  
  return dict({
      'status':status,
      'url': url,
      'content': content
    })