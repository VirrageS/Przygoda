import os

from flask import Flask, render_template, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, current_user
from flask.ext.mail import Mail

# set app
app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

# set database
db = SQLAlchemy(app)

# set mail
mail = Mail(app)

# if not debuging we should keep log of our app
if not app.config['DEBUG']:
	import logging
	from logging.handlers import RotatingFileHandler

	file_handler = RotatingFileHandler('tmp/przygoda.log', 'a', 1 * 1024 * 1024, 10)
	file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
	app.logger.setLevel(logging.INFO)
	file_handler.setLevel(logging.INFO)
	app.logger.addHandler(file_handler)
	app.logger.info('przygoda startup')

# secret key
def install_secret_key(application, filename='secret_key'):
	filename = os.path.join(application.instance_path, filename)

	try:
		application.config['SECRET_KEY'] = open(filename, 'rb').read()
	except IOError:
		print('Error: No secret key. Create it with:')
		full_path = os.path.dirname(filename)
		if not os.path.isdir(full_path):
			print('mkdir -p {filename}'.format(filename=full_path))
		print('head -c 24 /dev/urandom > {filename}'.format(filename=filename))
		sys.exit(1)


if not app.config['DEBUG']:
	install_secret_key(app)

# login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'  # path to login (handel 'required_login')
login_manager.login_message = 'Please log in to access this page'
login_manager.login_message_category = 'warning'

from app.users.models import User
@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))


@app.before_request
def before_request():
	g.user = current_user

# error handling
@app.errorhandler(404)
def not_found_error(error):
	return render_template('404.html', error=error), 404


@app.errorhandler(500)
def internal_error(error):
	db.session.rollback()
	return render_template('500.html', error=error), 500

# blueprint
from app.users.views import mod as usersModule
app.register_blueprint(usersModule)

from app.adventures.views import mod as adventuresModules
app.register_blueprint(adventuresModules)

from app.views import mod as modules
app.register_blueprint(modules)

from app.admin.views import mod as adminModules
app.register_blueprint(adminModules)

# Later on you'll import the other blueprints the same way:
# from app.comments.views import mod as commentsModule
# from app.posts.views import mod as postsModule
# app.register_blueprint(commentsModule)
# app.register_blueprint(postsModule)
