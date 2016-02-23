import requests # gets live data
from bs4 import BeautifulSoup # parses our html
import re
import urlparse # allows absolute link checking
import smtplib # sends email
from email.mime.text import MIMEText
import config # get config from config.py
import httplib, urllib # allows push
import dropbox # save directly to dropbox
import logging # keep record of what we do


def is_absolute(url):
	return bool(urlparse.urlparse(url).netloc)

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', filename='docsaver.log', level=logging.INFO) # setup logging to file

# Setup Dropbox connection
dbx = dropbox.Dropbox(config.dbAccessToken)


for pageObj in config.urls:

	for entry in dbx.files_list_folder(pageObj.dbdir).entries:
		print(entry.name)


	for link in notes_soup.findAll('a'):
		if is_absolute(link['href']):
			full_file_link = link['href']
			file_name = link['href'].rsplit('/', 1)[-1]
		else:
			full_file_link = pageObj.url.rsplit('/', 1)[0] + '/' + link['href']
			file_name = link['href']


		if link['href'] in dbx.files_list_folder(pageObj.dbdir).entries:
			print("found " + link['href'])
		else:
			print("not found")


		if full_file_link in open('saver_history.txt').read():
	 		continue # already saved this file, skip it

		with open('saver_history.txt', 'a') as historyfile:
			historyfile.write(full_file_link + '\n') # prevent repetitive saves


		# Send email with filename in body
		msg = MIMEText(full_file_link)
		msg['Subject'] = pageObj.tag + ' ' + link['href']
		msg['From'] = '*****@*****.com'
		msg['To'] = 'trigger@recipe.ifttt.com'

		s = smtplib.SMTP('smtp.gmail.com:587')
		s.starttls()  
		s.login('*****','*****')
		s.sendmail('*****@*****.com', ['trigger@recipe.ifttt.com'], msg.as_string())
		s.quit()