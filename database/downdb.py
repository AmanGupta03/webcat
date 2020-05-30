""" install database from google drive """

import gdown
import os  

url = 'https://drive.google.com/u/5/uc?export=download&confirm=KiTd&id=1-CTs6ZYTe1R16fBB72NyF8m0CUyIYHq_'

dir_path = os.path.dirname(os.path.realpath(__file__))
output = dir_path + '/web.db'
gdown.download(url, output, quiet=False)
