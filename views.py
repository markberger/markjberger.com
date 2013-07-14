import json
import hashlib
import hmac
from os import environ
from flask import Flask, render_template, abort, request
import time
from pymongo import MongoClient
from bson import json_util

POSTS_PER_PAGE = 4

app = Flask(__name__)

try:
	client = MongoClient(environ['MONGOHQ_URL'])
	db = client[environ['DB_NAME']]

except:
	print 'Error: Unable to connect to MongoHQ'
	db = None


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/projects/')
def projects():
	return render_template('projects.html')

@app.route('/blog/', defaults={'page':1})
@app.route('/blog/<int:page>/')
def blog_page(page):
	data = json.loads(get_posts(page), object_hook=json_util.object_hook)
	if data['request'] == 'error':
		abort(404)
	return render_template('page.html', posts=data['posts'],
										next_page=data['next_page'],
										prev_page=data['prev_page'])

@app.route('/blog/<title>')
def blog_post(title):
	post = db.blog.find_one({'url':title})
	if post is None:
		abort(404)
	else:
		return render_template('post.html', post=post)

@app.errorhandler(500)
def internal_error(exception):
	print exception

#-----------------------------
# Blog API
#-----------------------------

def api_error(error_str):
	return json.dumps({'request':'error', 'error':error_str})


def api_success():
	return json.dumps({'request':'success'})


def is_valid(data, recv_hash):
	if 'time' not in data:
		return False
	gen_hash = hmac.new(environ['BLOG_KEY'], data, hashlib.sha256).hexdigest()
	data = json.loads(data)
	time_diff = time.time() - data['time']
	if time_diff < -30 or time_diff > 60:
		print 'Request failed because time diff is:', time_diff
		return False
	elif recv_hash != gen_hash:
		print 'Request failed because the hashes do not match'
		return False
	else:
		return True


def add_post(post):
	post['url'] = '-'.join(post['title'].split(' ')).lower()
	try:
		db.blog.insert(post)
	except Exception as e:
		return False
	return True


@app.route('/api/new_post', methods=['POST'])
def new_post():
	data = request.form['json']
	recv_hash = request.form['hash']

	if is_valid(data, recv_hash):
		data = json.loads(data)
		data.pop('time')
		if add_post(data):
			return api_success()
		else:
			return api_error('Error adding post to database')
	else:
		return api_error('Invalid request')


@app.route('/api/get_posts', methods=['GET'])
def get_posts(page=1):
	if request.args:
		page = int(request.args['page'])
	if page <= 0:
		return api_error('Index out of range')
	posts = []
	cursor = db.blog.find(sort=[('date',-1)], skip=POSTS_PER_PAGE*(page-1), limit=POSTS_PER_PAGE)
	if POSTS_PER_PAGE*page - cursor.count() >= POSTS_PER_PAGE:
		return api_error('Index out of range')
	for post in cursor:
		json_post = json.dumps(post, default=json_util.default)
		dict_post = json.loads(json_post, object_hook=json_util.object_hook)
		posts.append(dict_post)
	data = {}
	data['posts'] = posts
	if page > 1:
		data['prev_page'] = page - 1
	else:
		data['prev_page'] = None
	if (cursor.count() - POSTS_PER_PAGE*page) > 0:
		data['next_page'] = page + 1
	else:
		data['next_page'] = None
	data['request'] = 'success'
	return json.dumps(data, default=json_util.default)


@app.route('/api/delete', methods=['POST'])
def delete_post():
	data = request.form['json']
	recv_hash = request.form['hash']
	if is_valid(data, recv_hash):
		data = json.loads(data)
		response = db.blog.remove({'url':data['url']})
		if not response['n']:
			return api_error('Could not find post to be deleted')
		else:
			return api_success()
	else:
		return api_error('Invalid request')


