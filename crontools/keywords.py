from sklearn.neighbors import NearestNeighbors
from crontools.globaldata import get_all_vectors, get_keyword_dict
from collections import OrderedDict
from tqdm import tqdm

def get_all_keywords(centroids):
  final_dict={}
  print("Finding all keywords ...")
  for i in tqdm(range(100)):
    num_of_neigh=50
    common_dict={}

    urlnvect=get_all_vectors(i)
    url_list=urlnvect['urls']
    vector_list=urlnvect['embedding']
    
    if len(vector_list)<10:
      num_of_neigh=len(vector_list)
    neigh = NearestNeighbors(num_of_neigh)
    neigh.fit(vector_list)

    index_list = neigh.kneighbors([centroids[i]], num_of_neigh, return_distance=False)
    
    for indexes in index_list[0]:
      word_dict=get_keyword_dict(url_list[indexes])
      tocommondict(word_dict,common_dict)
    final_dict[i]=final_words(common_dict)
  return final_dict


def tocommondict(word_dict,common_dict):
  for key in word_dict:
    if key not in common_dict:
      common_dict[key]=word_dict[key]
    else:
      common_dict[key]+=word_dict[key]


def final_words(common_dict):
  cluster_keywords={k: v for k, v in sorted(common_dict.items(), key=lambda item: item[1],reverse=True)}
  res = list(cluster_keywords.keys())[:10]
  listToStr =  ' '.join(res)
  return listToStr  