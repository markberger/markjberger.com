import os
from flaskext.markdown import Markdown
from views import app

Markdown(app)

def main():
    port = int(os.environ.get('PORT', 5000))
    app.config['DEBUG'] = os.environ.get('DEBUG', False)
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
