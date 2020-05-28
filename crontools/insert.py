from settings import DB_PATH
import sqlite3 

def insertData(data,tableName,scriptDate): 
  try:
    conn = sqlite3.connect(DB_PATH) 
    cur = conn.cursor()
    if(tableName=='keywords'):
      dataStr = dictToStrforkeywords(data)
    else:
      dataStr = dictToStr(data)
    colStr=getColStr()
    cur.execute("INSERT INTO "+str(tableName)+"("+colStr+")\
     VALUES ('"+scriptDate+"',"+dataStr+")")
    conn.commit()
  
  except sqlite3.Error as error:
      print(error)
    
  finally:
    if (conn): conn.close()


def getColStr():
  colStr="date_p"
  for i in range(100):
    colStr = colStr + ",c"+str(i)
  return colStr


def dictToStr(data):
  dataStr=""
  for x in range(99):
    dataStr = dataStr+''+str(data[x])+''+','
  dataStr = dataStr+''+str(data[99])+''
  return dataStr

def dictToStrforkeywords(data):
  dataStr=""
  for x in range(99):
    dataStr = dataStr+'"'+str(data[x])+'"'+','
  dataStr = dataStr+'"'+str(data[99])+'"'
  return dataStr
