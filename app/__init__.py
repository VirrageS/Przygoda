import os
import sys

from flask import Flask, render_template, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

# if not debuging we should keep log of our app
if not app.debug:
	import logging
	from logging.handlers import RotatingFileHandler
	file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1 * 1024 * 1024, 10)
	file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
	app.logger.setLevel(logging.INFO)
	file_handler.setLevel(logging.INFO)
	app.logger.addHandler(file_handler)
	app.logger.info('microblog startup')

########################
# Configure Secret Key #
########################
def install_secret_key(app, filename='secret_key'):
	"""Configure the SECRET_KEY from a file
	in the instance directory.

	If the file does not exist, print instructions
	to create it from a shell with a random key,
	then exit.
	"""
	filename = os.path.join(app.instance_path, filename)

	try:
		app.config['SECRET_KEY'] = open(filename, 'rb').read()
	except IOError:
		print('Error: No secret key. Create it with:')
		full_path = os.path.dirname(filename)
		if not os.path.isdir(full_path):
			print('mkdir -p {filename}'.format(filename=full_path))
		print('head -c 24 /dev/urandom > {filename}'.format(filename=filename))
		sys.exit(1)

if not app.config['DEBUG']:
	install_secret_key(app)

# Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from app.users.models import User
@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.before_request
def before_request():
	g.user = current_user

# Google maps
from flask.ext.googlemaps import GoogleMaps
GoogleMaps(app)

@app.errorhandler(404)
def not_found(error):
	return render_template('404.html'), 404

from app.users.views import mod as usersModule
app.register_blueprint(usersModule)

from app.adventures.views import mod as adventuresModules
app.register_blueprint(adventuresModules)

from app.views import mod as modules
app.register_blueprint(modules)

# Later on you'll import the other blueprints the same way:
#from app.comments.views import mod as commentsModule
#from app.posts.views import mod as postsModule
#app.register_blueprint(commentsModule)
#app.register_blueprint(postsModule)
