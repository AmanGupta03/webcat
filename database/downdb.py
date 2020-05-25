""" install database from google drive """

import gdown

url = 'https://drive.google.com/u/5/uc?export=download&confirm=KiTd&id=1TdiyzIEqXWIZ3m8BygxyLmErHSm6mzY8'

output = 'web.db'
gdown.download(url, output, quiet=False)