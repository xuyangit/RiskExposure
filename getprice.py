import urllib2
import json
import pymysql.cursors
from bs4 import BeautifulSoup

sqlCli = pymysql.connect(host='localhost',
                         user='root',
                         password='xuyang2008',
                         db='commodity',
                         charset='utf8mb4',
                         cursorclass=pymysql.cursors.DictCursor)

def get_html(_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    req = urllib2.Request(url=_url, headers=headers)
    html = urllib2.urlopen(req).read()
    return html

def getWtiNewestPrice():
    prices = json.loads(get_html("http://www.cmegroup.com/CmeWS/mvc/Quotes/Future/425/G?pageSize=50&_=1481173476449"))['quotes']
    for quote in prices:
        date = quote['expirationMonth']
        productCode = date[0:3] + date[6:8]
        productType = "WTI"
        price = quote['priorSettle']
        try:
            with sqlCli.cursor() as cursor:
                sql = "insert into `contractprice` (type, productCode, price) values ('{}', '{}', {}) on duplicate key update price={}".format(productType, productCode, price, price)
                cursor.execute(sql)
                sqlCli.commit()
        finally:
            print ""
if __name__=="__main__":
   getWtiNewestPrice()
   
