""" consist modules for search, similar_websites, keywords etc """

from settings import *
import pickle

def load_obj(filename):
  with open('./dump_obj/'+filename,'rb') as obj_file:
    obj = pickle.load(obj_file)
    return obj

print('loading kmeans..')
kmeans = load_obj("kmeans")