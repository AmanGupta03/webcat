""" install database from google drive """

import gdown
import os  

url = 'https://drive.google.com/u/5/uc?export=download&confirm=KiTd&id=1e06mw2hvDcMFsuC7UKhyVwFqHTDf4PGk'

dir_path = os.path.dirname(os.path.realpath(__file__))
output = dir_path + '/tempclustername.db'
gdown.download(url, output, quiet=False)
