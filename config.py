# Copyright Noah Benham, 2016
# Configuration file for Doc Saver Python script

class PageObj(object):
	def __init__(self,url,msg,dbdir):
		self.url=url
		self.msg=msg
		self.dbdir=dbdir


urls = {PageObj('http://people.eecs.ku.edu/~kinners/660web/notes/notes_index.html',
				'Kinnersley posted a new note',
				'/Documents/KU/EECS 660/Notes'),
		PageObj('http://people.eecs.ku.edu/~kinners/660web/homework/hw_index.html',
				'Kinnersley posted new homework',
				'/Documents/KU/EECS 660/Homework')
		}

pushover = dict(
	apptoken = '<APP TOKEN HERE>',
	userkey = '<USER KEY HERE>'
	)

dbAccessToken = '<DB ACCESS TOKEN>'