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

def prep_request(data):
	data['time'] = time.mktime(time.gmtime())
	request_data = json.dumps(data)
	h = hmac.new(API_KEY, request_data, hashlib.sha256)
	to_send = 'hash=' + h.hexdigest() + '&json=' + request_data
	return to_send

def get_posts(page=1):
	req = urllib2.Request(BLOG_URL+'api/get_posts?page=%d' % int(page))
	response = json.load(urllib2.urlopen(req))
	print response

def delete(post_path):
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
			print 'Successfully deleted:', data['url']
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


if __name__ == '__main__':
	parser = argh.ArghParser()
	parser.add_commands([upload, delete, get_posts])
	parser.dispatch()
