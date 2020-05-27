""" consist modules for search, similar_websites, keywords etc """

from settings import *
import numpy as np 
import pickle


def load_obj(filename):
  """ to load file from dump_obj """
  with open('./dump_obj/'+filename,'rb') as obj_file:
    obj = pickle.load(obj_file)
    return obj


def make_neigh_matrix():
  """ return neighbour matrix for centroifs of cluster """

  centroid = kmeans.cluster_centers_
  neigh = np.zeros(shape=(MAX_CLUSTER, MAX_CLUSTER-1), dtype=int)
  
  for i in range(MAX_CLUSTER):
    pass
    dist = []
    for j in range(MAX_CLUSTER):
      if i != j:
        dist.append([np.linalg.norm(centroid[i]-centroid[j]), j])
    dist.sort()
  
    for j in range(MAX_CLUSTER-1):
      neigh[i][j] = dist[j][1]
  
  return neigh  

print('loading kmeans..')

kmeans = load_obj("kmeans")

neigh = make_neigh_matrix()
