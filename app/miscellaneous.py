from functools import wraps
from flask.ext.login import current_user
from flask import redirect, url_for, flash

def confirmed_email_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if (current_user is None) or (current_user.confirmed is False):
			flash('Musisz potwierdzic swoj email zeby skorzystac z tej funkcji', 'danger')
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
			return error_response()

		return f(*args, **kwargs)
	return wrapper
