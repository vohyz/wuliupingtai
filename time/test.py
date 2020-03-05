import requests
import json, urllib
from urllib import parse
from urllib.request import urlopen


def request1(m="GET"):
    url = "http://127.0.0.1:5003"
    params = {
            "Time": '10 10 10 10',
            "ID": '100003'
        }
    params = parse.urlencode(params)
    if m == "GET":
        f = urlopen("%s?%s" % (url, params))
    else:
        f = urlopen(url, params)
    content = f.read()
    res = json.loads(content)
    print(res)

if __name__ == '__main__':
    request1()