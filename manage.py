import argh
import os
import json
import hashlib
import hmac
import urllib2
from datetime import date
import time
import yaml
from settings import API_KEY, BLOG_URL
import ConfigParser
import subprocess

def prep_request(data):
	data['time'] = time.time()
	request_data = json.dumps(data)
	h = hmac.new(API_KEY, request_data, hashlib.sha256)
	to_send = 'hash=' + h.hexdigest() + '&json=' + request_data
	return to_send

def get_posts(page=1):
	req = urllib2.Request(BLOG_URL+'api/get_posts?page=%d' % int(page))
	response = json.load(urllib2.urlopen(req))
	for post in response['posts']:
		print "\t" + post['title'] + ' (%s)' % post['date_str']

def remove(post_path):
	post_path = 'posts/' + post_path
	if os.path.isfile(post_path):
		data = {}
		stream = file(post_path, 'r')
		post = yaml.load(stream)
		data['url'] =  '-'.join(post['title'].split(' ')).lower()
		to_send = prep_request(data)
		req = urllib2.Request(BLOG_URL+'api/delete', data=to_send)
		response = json.load(urllib2.urlopen(req))

		if response['request'] == 'success':
			print 'Successfully removed:', data['url']
		else:
			print 'Encountered error:', response['error']
	else:
		print 'Could not find:', post_path

def upload(post_path):
	post_path = 'posts/' + post_path
	if os.path.isfile(post_path):
		stream = file(post_path, 'r')
		post = yaml.load(stream)
		post['date'] = time.mktime(post['date'].timetuple())
		to_send = prep_request(post)
		req = urllib2.Request(BLOG_URL+'api/new_post', data=to_send)
		response = json.load(urllib2.urlopen(req))

		if response['request'] == 'success':
			print 'Successfully uploaded:', post_path
		else:
			print 'Encountered error:', response['error']
	else:
		print 'Could not find:', post_path

def new(name='new_post'):
	path = 'posts/'+name+'.yaml'
	if os.path.isfile(path):
		print '\'%s\' already exists. Please choose a different name.' % path
	else:
		f = open('posts/'+name+'.yaml', 'w+')
		f.write("title:\n")
		f.write("date: %s\n" % date.today())
		f.write("date_str:\n")
		f.write("body: |\n    \n")
		f.write("tags:\n    -")
		f.close()

def init():
	config = ConfigParser.ConfigParser()
	config.optionxform = str
	config.add_section('global')
	config.set('global', 'BLOG_KEY', '')
	config.set('global', 'MONGOHQ_URL', '')
	config.set('global', 'DB_NAME', '')
	config.add_section('production')
	config.set('production', 'FLASK_ENV', 'production')
	config.set('production', 'DEBUG', 'False')
	config.add_section('local')
	config.set('local', 'FLASK_ENV', 'development')
	config.set('local', 'DEBUG', 'True')

	with open('settings-test.ini', 'w+') as configfile:
		config.write(configfile)

def freeze():
	config = ConfigParser.ConfigParser()
	config.optionxform = str
	f = open('settings.ini')
	config.readfp(f)
	f.close()

	global_opts = config.items('global')
	production_opts = config.items('production')
	local_opts = config.items('local')

	print 'Settings local config vars..'
	f = open('.env', 'w+')
	for pair in global_opts + local_opts:
		f.write(pair[0]+'='+pair[1]+'\n')

	args = "heroku config:set"
	for pair in global_opts + production_opts:
		args += " %s=%s" % (pair[0], pair[1])
	subprocess.call(args, shell=True)

if __name__ == '__main__':
	parser = argh.ArghParser()
	parser.add_commands([upload,
						 remove,
						 get_posts,
						 new,
						 freeze,
						 init])
	parser.dispatch()
