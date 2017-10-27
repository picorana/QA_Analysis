# TODO:
# * import list of asins from file
# * ability to change proxy sources 

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from pprint import pprint
import requests
import random
import logging
import argparse
import threading, Queue
import time
import json
import re
import os, sys

base_product_page_url = 'https://www.amazon.com/gp/product/'

class AmazonScraper(object):
	"""Hello, this is AmazonScraper!"""

	def __init__(self, **kwargs):

		default_attr = dict(
			asin = '',
			asins = [],
			verbose=2
			)

		self.logger = AmazonScraper.get_logger(level=logging.INFO, verbose=default_attr.get('verbose'))

		allowed_attr = list(default_attr.keys())
		default_attr.update(kwargs)

		for key in default_attr:
			if key in allowed_attr: self.__dict__[key] = kwargs.get(key)

		# initialize a user agent generator
		self.ua = UserAgent()
		self.wait_time = 0.2


	def scrape(self):
		"""Manages the whole scraping process"""

		for asin in self.asin:

			self.logger.info("Examining product " + asin)

			self.proxies = self.get_proxies()

			main_reviews_url = self.retrieve_page(asin)


	def retrieve_page(self, asin):
		"""Requests the main product page, saves it, and returns an url for the reviews"""

		attempt = 0

		while attempt < 10: 

			res = requests.get(base_product_page_url + asin, 
				proxies = { 'http' : random.sample( self.proxies, 1 )},
				headers = { 'User-Agent' : self.ua.random}
				)

			if res.status_code == 404:
				self.logger.error("Asin " + asin + " does not exist")
				raise RuntimeError("Asin " + asin + " does not exist")
			elif res.status_code != 200:
				self.logger.error("Connection error on asin " + asin)
			else:

				page_file = open("./pages/" + asin + '.html', 'w+')
				page_file.write(res.content)

				soup = BeautifulSoup(res.content, 'html.parser')

				if soup.title.text == "Robot Check":
					self.logger.log("Robot Check received")

				return soup.find(
					"div", { "id" : "reviews-medley-footer" }
					).find(
					"a", { "class" : "a-link-emphasis" }
					).get("href")







	def get_proxies(self):
		"""Retrieves a list of proxies"""

		proxies = set()

		proxy_sources = [
			'https://free-proxy-list.net/anonymous-proxy.html', 
			'https://www.us-proxy.org/', 
            'https://www.sslproxies.org/', 
            'https://www.socks-proxy.net/'
		]

		attempt = 0
		while not len(proxies) > 0:
			for source in proxy_sources:
				res = requests.get(source, headers={
					'User-Agent':self.ua.random
					})

				if res.status_code != 200:
					self.logger.error("connection error " + str(res.status_code) \
						+ " source " + source)
				else:
					soup = BeautifulSoup(res.content, 'html.parser')
					tab = soup.find("table", {"id":"proxylisttable"})
					for cell in tab.find_all('td'):
						if cell.string != None and re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', cell.string) != None: 
							proxies.add(cell.string)
			
			self.logger.info("found " + str(len(proxies)) + " proxies")

			if not len(proxies) > 0:
				attempt += 1
				if attempt >= 10:
					raise ConnectionError("Failed to \
						retrieve any proxy after several \
						attempts, check your connection status")
				time.sleep(0.5)
			else:
				break

		return proxies


	@staticmethod
	def get_logger(level=logging.INFO, verbose=2):
		"""Returns a logger"""

		logger = logging.getLogger(__name__)

		fh = logging.FileHandler('scrape.log', 'wa')
		fh.setFormatter( logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') )
		fh.setLevel(level)
		logger.addHandler(fh)

		sh = logging.StreamHandler(sys.stdout)
		sh.setFormatter( logging.Formatter('%(levelname)s: %(message)s') )
		sh_lvls = [logging.ERROR, logging.WARNING, logging.INFO]
		sh.setLevel(sh_lvls[verbose])
		logger.addHandler(sh)

		logger.setLevel(level)

		return logger

	



def main():

	parser = argparse.ArgumentParser(
		description = "this is amazon_scraper",
		formatter_class = argparse.RawDescriptionHelpFormatter,
		fromfile_prefix_chars='@'
		)

	parser.add_argument('asin', help='Amazon asin(s) to be scraped', nargs='*')
	parser.add_argument('--filename', '-f', help='Specify path to list of asins')

	args = parser.parse_args()
	
	if args.asin is None and args.filename is None:
		parser.print_help()
		raise ValueError('Please provide asin or filename.')
	elif args.asin and args.filename:
		parser.print_help()
		raise ValueError('Please provide only one of the following: asin(s) or filename')
	
	scraper = AmazonScraper(**vars(args))

	scraper.scrape() 

if __name__ == '__main__':
	main()