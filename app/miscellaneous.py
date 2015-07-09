from functools import wraps
from flask.ext.login import current_user
from flask import redirect, url_for, flash, abort
from app.users import constants as USER

def confirmed_email_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if (current_user is None) or (current_user.confirmed is False):
			flash('Musisz potwierdzic swoj email zeby skorzystac z tej funkcji', 'danger')
			return redirect(url_for('simple_page.index'))

		return f(*args, **kwargs)
	return wrapper

def not_login_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if current_user.is_authenticated():
			return redirect(url_for('simple_page.index'))

		return f(*args, **kwargs)
	return wrapper

def ssl_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if current_app.config.get("SSL"):
			if request.is_secure:
				return f(*args, **kwargs)
			else:
				return redirect(request.url.replace("http://", "https://"))

		return f(*args, **kwargs)
	return wrapper

# Usage @rule_required('admin', 'user')
def rule_required(*roles):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if str(current_user.role) not in roles:
			return abort(404)

		return f(*args, **kwargs)
	return wrapper

def admin_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if (not current_user.is_authenticated()) or (current_user.role != USER.ADMIN):
			return abort(404)

		return f(*args, **kwargs)
	return wrapper

def add_admin():
	# add admin
	from app.users.models import User
	from werkzeug import generate_password_hash
	from app.users import constants as USER
	from app import db

	u = User.query.filter_by(username="admin").first()
	if u is None:
		u = User("admin", generate_password_hash("supertajnehaslo"), "email@email.com", social_id=None)
		u.role = USER.ADMIN
		u.confirmed = True
		db.session.add(u)
		db.session.commit()
