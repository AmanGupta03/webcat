"""
package to scrap text content from website, and preprocessing

"""

__all__ = ['dictionary', 'lemma', 'embd', 'AVOID',  'DIMENSION', 'MAX_WORDS']

from settings import *
import sqlite3 

def get_words_data():
  """ return dictionary, lemma and embedding from dictionary table """
  
  print('loading word vectors...')
  
  try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    rows = cur.execute('SELECT * from dictionary')

    dictionary, lemma, embd = set(), {}, {}

    for row in rows:
      dictionary.add(row[0])
      lemma[row[0]] = row[2]
      embd[row[0]] = row[1]
    
    return dictionary, lemma, embd

  except sqlite3.Error as error:
    print('error loading words data', error)

"""
dictionary -: set of all allowed words
lemma -: dict consist mapping of words with their lemma
embd -: dict consist mapping of words with their embedding in bytes

"""

dictionary, lemma, embd = get_words_data()

#Frequent Terms find on web
AVOID = {'error', 'enable', 'jump', 'rights', 'block', 'condition', 'javascript', 'fail', 'menu', 'filipino', 'register', 'site', 'request', 'dutch', 'espanol', 'reserved', 'help', 'home', 'url', 'italiano', 'page', 'navigate', 'cookie', 'browser', 'disable', 'cancel', 'unsupported', 'english', 'francais', 'login', 'privacy', 'term', 'section', 'disabled', 'skip', 'main', 'copyright', 'uses', 'navigation', 'more', 'anymore', 'log', 'open', 'homepage', 'corona', 'policy', 'content', 'terms', 'sign', 'upgrade', 'portugal', 'older', 'require', 'know', 'indonesia', 'support', 'results', 'language', 'coronavirus', 'best', 'load', 'deutsch', 'cookies'}

#dimension of word vector used
DIMENSION = 50