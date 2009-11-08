#!/usr/bin/env python2.5

import csv, sys, os, getpass, time

DIR_PATH = '/usr/local/google_appengine/'

EXTRA_PATHS = [
  DIR_PATH,
  os.path.join(DIR_PATH, 'lib', 'antlr3'),
  os.path.join(DIR_PATH, 'lib', 'django'),
  os.path.join(DIR_PATH, 'lib', 'webob'),
  os.path.join(DIR_PATH, 'lib', 'yaml', 'lib'),
	os.path.realpath(__file__)
]
sys.path = EXTRA_PATHS + sys.path

from google.appengine.ext import db
from google.appengine.ext.remote_api import remote_api_stub
import models
import geobox


CSVFIELDS = ['tree_id', 'legal_status', 'species', 'address', 'tree_order',
						 'site_type', 'plant_type', 'caretaker', 'care_assistant',
						 'planting_date', 'dbh', 'plot_size', 'permit_notes',
						 'longitude', 'latitude']



def auth_func():
  return (raw_input('Username:'), getpass.getpass('Password:'))

timers = {}
def timer_start(timer_name):
	timers[timer_name] = time.time()

def timer_end(timer_name):
	print "%s: %s" % (timer_name, time.time() - timers[timer_name])
	del timers[timer_name]
	

def main():
	#TODO(bheilbrun): servername option
	remote_api_stub.ConfigureRemoteDatastore('sf-trees',
																					 '/remote_api',
																					 auth_func,
#																					 servername='localhost:8080')
																					 servername='sf-trees.appspot.com')

	timer_start('csv_reader')
	reader = csv.reader(open(sys.argv[1]), quotechar='"')
	timer_end('csv_reader')
	entity_list = []
	for tree in reader:
		d = dict(zip(CSVFIELDS, tree))
		#timer_start('entity_create')
		entity_list.append(models.SFTree.create(**d))
		#timer_end('entity_create')

		if len(entity_list) > 100:
			timer_start('db.put')
			rc = db.put(entity_list)
			timer_end('db.put')
			entity_list = []
			print "Wrote %s records." % len(rc)

if __name__ == '__main__':

	main()
