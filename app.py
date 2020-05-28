"""

  Note-: all routes are adjusted by assuming cluster_no start with 1 for end_user
        all other modules assuming 0 based indexing of cluster no.

"""

print('initializing...')

from flask import Flask
from flask_cors import CORS, cross_origin
from datetime import date, timedelta
from flask import Flask
import urllib.parse
import json
import os
from webdata.trendsdata import get_all_info, cluster_info_bw_date,allClusterData,keywords_by_cluster
from webdata.globaldata import get_cluster_websites,site_info_by_cluster
from webtools.search import search_by_domain, search_by_query,update_cluster_name
from webtools.processurl import get_processed_info
from settings import *
from webtools import kmeans
from numpy.linalg import norm

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = '*'


ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
print('READY')


@app.route('/<path:url>')
@app.route('/')
@cross_origin()

def result_url(url=''):
    print(url)
    return get_processed_info(url)

@app.route('/<path:url>/<int:status>')
@app.route('/')
@cross_origin()
def result_url1(status,url=''):
#@app.route('/<path:url>')
#@app.route('/')
#@cross_origin()
#def result_url(url=''):
    print(url)
    return get_processed_info(url,status)

@app.route('/getclusterurl/page/<int:page_no>')
@app.route('/getclusterurl/<int:cluster_no>/page/<int:page_no>')
@cross_origin()
def get_cluster_url(cluster_no=0,page_no=0):
    if cluster_no <=0 or cluster_no >100:
        return json.dumps(get_cluster_websites(page_no,cluster_no-1))
    else:
        return json.dumps(get_cluster_websites(page_no,cluster_no-1))

@app.route('/search/query/<q>/clusterno/<int:cluster_no>')
@app.route('/search/query/<q>')
@cross_origin()

def query_search(q,cluster_no=0):
    q=urllib.parse.unquote(q).split(" ")
    print(q)
    return json.dumps(search_by_query(q,cluster_no-1))

@app.route('/search/domain/<q>')
@cross_origin()
def domain_search(q):
    q=urllib.parse.unquote(q).split(" ")
    return json.dumps(search_by_domain(q))

@app.route('/getinfo/')
@cross_origin()
def get_info_route():
    return json.dumps(get_all_info())

@app.route('/getClusterData/<startDate>/<endDate>/<int:cluster_no>')
@cross_origin()
def getClusterData(startDate,endDate,cluster_no):
  if(startDate<DB_FIRST_DATE):
    startDate = DB_FIRST_DATE
  if(endDate>DB_DATE):
    endDate = DB_DATE
  return json.dumps(cluster_info_bw_date(cluster_no-1, startDate,endDate))
  #return []


@app.route('/getOneDayClusterData/<endDate>/<int:cluster_no>')
@cross_origin()
def getOneDayClusterData(endDate,cluster_no):
  try:
    if(endDate>DB_DATE):
      endDate = DB_DATE
    startDate=str(date(int(endDate[0:4]),int(endDate[5:7]),int(endDate[8:10]))-timedelta(days=1))
    print("one day cluster day data",startDate, endDate)
    newDictList = cluster_info_bw_date(cluster_no-1, startDate,endDate)
    if(newDictList[0]['date']==str(endDate) or newDictList[-1]['date']==str(endDate)):
      clusterData={}
      clusterData['date']=endDate
      clusterData["rank"]=int(newDictList[-1]['rank'])
      clusterData["size"]=newDictList[-1]['size']
      clusterData["keywords"]=newDictList[-1]["keywords"]
      clusterData['rankChange']=clusterData["rank"]
      clusterData['sizeChange']=clusterData["size"]
      if(newDictList[0]['date']==str(startDate)):
        clusterData["rankChange"]-=int(int(newDictList[0]['rank']))
        clusterData["sizeChange"]-=int(newDictList[0]['size'])
      return json.dumps([clusterData])
    else:
      return json.dumps([])
  except Exception as e:
    print("Error with one date Cluster Data api ",e)
    return json.dumps([])

@app.route('/getClusterInfo/<int:cluster_no>')
@cross_origin()
def getClusterInfo(cluster_no):
  try:
    keywords=keywords_by_cluster(cluster_no)
    centroids = kmeans.cluster_centers_
    sites = sorted([(norm(row[1]-centroids[cluster_no-1]), row[0], row[3] if row[3] != -1 else DB_DEFAULT_RANK) for row in site_info_by_cluster(cluster_no)], key=lambda x: x[0])
    final= sorted([{'url': v[1], 'rank': v[2]} for v in sites[:10]], key=lambda x: x['rank'])
    only_urls=[ dict['url'] for dict in final ] 
    return {'keywords':keywords,'urls':only_urls}
  except sqlite3.Error as error:
    print('error fetching data from site_info', error)
    return json.dumps([])


@app.route('/getAllClusterDataOfSize/<Date>')
def getAllClusterDataOfSize(Date):
    return json.dumps(allClusterData(Date,'SIZE'))
  
@app.route('/getAllClusterDataOfRank/<Date>')
def getAllClusterDataOfRank(Date):
    return json.dumps(allClusterData(Date,'RANK'))
 
@app.route('/updateClusterName/<int:cluster>/<name>')
def updateClusterName(cluster,name):
    update_cluster_name(cluster,name)
    return "SUCCESSFULLY ADDED NEW RECORDS"

if __name__ == '__main__':
    app.run(host= '0.0.0.0',use_reloader=False,debug=True)
