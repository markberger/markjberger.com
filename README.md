#markjberger.com

This is my personal website. It runs on Flask with a MongoDB backend for my blog and it's hosted on Heroku. 
New blog posts are written in yaml files and then pushed to the server using a json api. Access to the api 
is limited using hash-based message authentication (HMAC). A time stamp is added to each api request in order to
prevent replay attacks.

#To Do:
- Make time_diff change according to whether site is running in development or production
- manage.py: get_posts should download and store posts in yaml files
- manage.py: Write a function that will create a new yaml file with all of the required fields
- Add tags to the blog
- Add an atom/rss feed
