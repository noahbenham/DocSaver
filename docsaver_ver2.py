import requests # gets live data
from bs4 import BeautifulSoup # parses our html
import re
import urlparse # allows absolute link checking
import config # get config from config.py
import httplib, urllib # allows push
import dropbox # save directly to dropbox
import logging # keep record of what we do

def is_absolute(url):
	return bool(urlparse.urlparse(url).netloc)

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', filename='docsaver.log', level=logging.INFO)

for pageObj in config.urls:

	currentpage = requests.get(pageObj.url)
	soup = BeautifulSoup(currentpage.text, "html5lib") # parse page with BeautifulSoup

	for link in soup.findAll('a'):
		# Test if the URL from the page is an asbolute link or not
		if is_absolute(link['href']): # Already have full (absoulte) link, just generate filename
			full_file_link = link['href']
			file_name = link['href'].rsplit('/', 1)[-1]
		else: # Already have filename, just generate full (absolute) link
			full_file_link = pageObj.url.rsplit('/', 1)[0] + '/' + link['href']
			file_name = link['href']

		# File name was previously a URL - make it human readable
		file_name = urllib.unquote(file_name).decode('utf8')


		if full_file_link in open('saver_history.txt').read():
			continue # already saved this file, skip it

		with open('saver_history.txt', 'a') as historyfile:
			historyfile.write(full_file_link + '\n') # prevent repetitive saves

		# Save this file to Dropbox using the absolute URL
		req = requests.post('https://api.dropboxapi.com/1/save_url/auto/{}/{}'.format(pageObj.dbdir, file_name),
			headers={'Authorization': 'Bearer {}'.format(config.dbAccessToken)},
			data={'url': full_file_link})

		# print(req.text)


		# Send Pushover notification
		conn = httplib.HTTPSConnection("api.pushover.net:443")
		conn.request("POST", "/1/messages.json",
			urllib.urlencode({
				"token": config.pushover['apptoken'],
				"user": config.pushover['userkey'],
				"message": pageObj.msg,
				"url": full_file_link,
			}), { "Content-type": "application/x-www-form-urlencoded" })
		conn.getresponse()