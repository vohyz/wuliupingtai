import requests
import json, urllib
from urllib import parse
from urllib.request import urlopen

class Order_Test():

    def createOrder(self,m="GET"):
        url = "http://127.0.0.1:5001"
        params = {
            'order_begin_name': '小明',
            'order_begin_phone': '15316172791',
            'order_begin_city': '上海',
            'order_end_name': '小红',
            'order_end_phone': '01987654321',
            'order_end_city': '杭州'
        }
        params = parse.urlencode(params)
        if m == "GET":
            f = urlopen("%s?%s" % (url, params))
        else:
            f = urlopen(url, params)
        content = f.read()
        res = json.loads(content)
        print(res)

    def searchOrder(self):
        url = "http://127.0.0.1:5001/searchbyOrder"
        params = {
            'order_id': order_id
        }
        params = parse.urlencode(params) 

        f = urlopen("%s?%s" % (url, params))

        content = f.read()
        res = json.loads(content)
        print(res)


if __name__ == '__main__':
    test = Order_Test()
    # test.createOrder()
    # test.searchOrder()