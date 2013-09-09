import os
from flaskext.markdown import Markdown
from views import app

Markdown(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
