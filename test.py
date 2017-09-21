# Simple Amazon API: https://github.com/yoavaviram/python-amazon-simple-product-api
from amazon.api import AmazonAPI
import urllib2
import requests

"""
proxy = urllib2.ProxyHandler({'https': '149.56.40.69'})
opener = urllib2.build_opener(proxy)
urllib2.install_opener(opener)
print urllib2.urlopen('http://www.google.com').read()
"""

url = 'http://www.google.com'
proxy = '103.249.180.163'
print requests.get(url, proxies={"http":proxy})

"""
f = open("keys.txt", 'r')
AMAZON_ASSOC_TAG = f.readline().strip().split("=")[1]
AMAZON_ACCESS_KEY = f.readline().strip().split("=")[1]
AMAZON_SECRET_KEY = f.readline().strip().split("=")[1]

amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG, region="US")
product = amazon.lookup(ItemId='B00E5FJTPI')
print product.title


from bs4 import BeautifulSoup

res = urllib2.urlopen(rev[1]).read()

soup = BeautifulSoup(res, 'html.parser')
divs = soup.findAll("div", { "class" : "reviewText" })
for d in divs: 
	print d
"""