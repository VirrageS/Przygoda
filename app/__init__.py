import os
import sys

from flask import Flask, render_template, g, request, send_from_directory
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, current_user
from flask.ext.mail import Mail
from flask.ext.cache import Cache
from flask.ext.babel import Babel, lazy_gettext
from celery import Celery

# set app
app = Flask(__name__)

if os.environ.get('CONFIG'):
	app.config.from_object('config.' + os.environ.get('CONFIG') + 'Config')
else:
	app.config.from_object('config.DevelopmentConfig')

# set database
db = SQLAlchemy(app)

# set mail
mail = Mail(app)

# set babel (language)
babel = Babel(app)

# cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# celery
def make_celery(app):
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

# if not debuging we should keep log of our app
if not app.config['DEBUG']:
	import logging
	from logging.handlers import RotatingFileHandler

	try:
		file_handler = RotatingFileHandler('logs/przygoda.log', 'a', 1 * 1024 * 1024, 10)
		file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
		app.logger.setLevel(logging.INFO)
		file_handler.setLevel(logging.INFO)
		app.logger.addHandler(file_handler)
		app.logger.info('przygoda startup')
	except:
		print('Probably missing logs folder' + str(sys.exc_info()[0]))

# secret key
def install_secret_key(application, filename='secret_key'):
	filename = os.path.join(application.instance_path, filename)

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
	pass
	# install_secret_key(app)

from flask.json import JSONEncoder

class CustomJSONEncoder(JSONEncoder):
    """This class adds support for lazy translation texts to Flask's
    JSON encoder. This is necessary when flashing translated texts."""
    def default(self, obj):
        from speaklater import is_lazy_string
        if is_lazy_string(obj):
            return str(obj)
        return super(CustomJSONEncoder, self).default(obj)

app.json_encoder = CustomJSONEncoder

@babel.localeselector
def get_locale():
	language = request.accept_languages.best_match(['pl', 'en'])
	if (language is not None) and language:
		app.config['BABEL_DEFAULT_LOCALE'] = language

	return language

# login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'  # path to login (handel 'required_login')
login_manager.login_message = lazy_gettext(u'Please log in to access this page')
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

from app.api.views import mod as apiModules
app.register_blueprint(apiModules)

# Later on you'll import the other blueprints the same way:
# from app.comments.views import mod as commentsModule
# from app.posts.views import mod as postsModule
# app.register_blueprint(commentsModule)
# app.register_blueprint(postsModule)
