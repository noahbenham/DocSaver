# Copyright Noah Benham, 2016
# Auto-saver for class files. Settings are in config.py.

import requests # gets live data
from bs4 import BeautifulSoup # parses our html
import config # get config from config.py
import urllib.request, urllib.parse, urllib.error # allows push
import logging # keep record of what we do
import json # allows parsing of dropbox response
import os # get environment variables
import time

dbAccessToken = os.getenv('DOCSAVER_DB_ACCESSTOKEN')
pushoverAppToken = os.getenv('DOCSAVER_PUSHOVER_APPTOKEN')
pushoverUserKey = os.getenv('PUSHOVER_USERKEY')

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', filename='docsaver.log', level=logging.DEBUG)


if dbAccessToken is None:
	logging.error("[ERROR] Dropbox token could not be found")
if pushoverAppToken is None:
	logging.error("[ERROR] Pushover app token could not be found")
if pushoverUserKey is None:
	logging.error("[ERROR] Pushover user key could not be found")

def is_absolute(url):
	return bool(urllib.parse.urlparse(url).netloc)

try: # create history file if it does not exist
	open('saver_history.txt', 'x')
	logging.info('History file does not exist, created file.')
except:
	logging.debug('Successfully found existing history file.')

for pageObj in config.urls:
	currentpage = requests.get(pageObj.url)
	soup = BeautifulSoup(currentpage.text, "html5lib") # parse page with BeautifulSoup

	for file_name in set(link.get('href') for link in soup.findAll('a')): # only save unique URLs
		# Test if the URL from the page is an asbolute link or not
		if is_absolute(file_name): # Already have full (absoulte) link, just generate filename
			full_file_link = file_name
			file_name = file_name.rsplit('/', 1)[-1]
		else: # Already have filename, just generate full (absolute) link
			full_file_link = pageObj.url.rsplit('/', 1)[0] + '/' + file_name

		
		historyfile = open('saver_history.txt', 'r+')
		for line in historyfile:
			if full_file_link in line:
				logging.info("Found {} in history file, will not save to Dropbox.".format(file_name))
				break # already saved this file, skip it
		else:
			logging.info("Could not find link in history file, will continue running script.")
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

			historyfile.seek(0,2) # move to end of file
			historyfile.write(full_file_link + '\n') # prevent repetitive saves