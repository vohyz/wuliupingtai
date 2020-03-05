import requests
import json, urllib
from urllib import parse
from nameko.rpc import rpc
from urllib.request import urlopen
import pymysql

def login(userphone, sms_code, m="GET", ):
    url = "http://39.107.229.211:5001/login"
    params = {
        'name': userphone,
        "pass": sms_code
    }
    params = parse.urlencode(params)
        
    f = urlopen("%s?%s" % (url, params))
        
    content = f.read()
    res = json.loads(content)
    print(res)

def connect_mysql():#链接mysql
    conn = pymysql.connect(host="cdb-518aglpe.bj.tencentcdb.com", port=10101, user="root", password="zyx1999zyx", database="service")
    cursor = conn.cursor()
    return conn,cursor
def add(userphone, address):
    conn,cursor = connect_mysql()           # 连接到mysql
    print(address)
    sql = 'INSERT INTO user_address VALUES (%s, %s)'%(userphone, address)
    print(sql)
    cursor.execute(sql) 
    
    conn.commit()
    cursor.close()
    conn.close()                   # 此处需要补异常处理，限于时间原因以后再补
    return 'ok'
if __name__ == '__main__':
    # login('123','123')
    # a = rpc.greeting_service.hello(name='jerry')
    add('15316172791', '"f"')