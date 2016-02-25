# Copyright Noah Benham, 2016
# Auto-saver for class files. Settings are in config.py.

import requests # gets live data
from bs4 import BeautifulSoup # parses our html
import config # get config from config.py
import urllib.request, urllib.parse, urllib.error # allows push
import logging # keep record of what we do
import json # allows parsing of dropbox response
import os

dbAccessToken = os.getenv('DOCSAVER_DB_ACCESSTOKEN')
pushoverAppToken = os.getenv('DOCSAVER_PUSHOVER_APPTOKEN')
pushoverUserKey = os.getenv('PUSHOVER_USERKEY')

if dbAccessToken is None:
	logging.error("[ERROR] Dropbox token could not be found")
if pushoverAppToken is None:
	logging.error("[ERROR] Pushover app token could not be found")
if pushoverUserKey is None:
	logging.error("[ERROR] Pushover user key could not be found")

def is_absolute(url):
	return bool(urllib.parse.urlparse(url).netloc)

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', filename='docsaver.log', level=logging.ERROR)


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


		if full_file_link in open('saver_history.txt', 'r+').read():
			continue # already saved this file, skip it


		file_name = urllib.parse.unquote(file_name) # make filename readable, e.g. %20 becomes ' '

		# Attempt saving file to Dropbox
		req = requests.post('https://api.dropboxapi.com/1/save_url/auto/{}/{}'.format(pageObj.dbdir, file_name),
			headers={'Authorization': 'Bearer {}'.format(dbAccessToken)},
			data={'url': full_file_link})

		# Make sure the file saved successfully
		jsonResponse = json.loads(req.text)
		if 'error' in jsonResponse:
			logging.error("Error saving file to Dropbox, response was: {}".format(jsonResponse['error']))
			continue # break out of loop, continue to next file

		dbSaveStatus = 'PENDING'
		while(dbSaveStatus != 'COMPLETE' and dbSaveStatus != 'FAILED'): # loop until success or failure
			req = requests.post('https://api.dropboxapi.com/1/save_url_job/{}'.format(jsonResponse['job']),
				headers={'Authorization': 'Bearer {}'.format(dbAccessToken)})
			dbSaveStatus = json.loads(req.text)['status']

		# Report save status in notification
		noti_msg = pageObj.msg.strip(' ') + ' ' + file_name
		if dbSaveStatus == 'COMPLETE':
			noti_msg += ". Saved to Dropbox."
		else:
			noti_msg += ". ERROR saving to Dropbox."


		# Send Pushover notification
		url = 'https://api.pushover.net:443/1/messages.json'
		payload = {'token': pushoverAppToken, 'user': pushoverUserKey,
				   'message': noti_msg, 'url': full_file_link}
		r = requests.post(url, params=payload)
		logging.info("Sent message '{}' to user via Pushover".format(noti_msg))

		with open('saver_history.txt', 'a') as historyfile:
			historyfile.write(full_file_link + '\n') # prevent repetitive saves