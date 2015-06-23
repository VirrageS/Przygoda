import datetime
from werkzeug import check_password_hash, generate_password_hash
from flask import Blueprint, request, render_template, g, flash, redirect, url_for
from flask.ext.login import current_user, login_user, logout_user, login_required
from flask.ext.sqlalchemy import get_debug_queries

from app import app, db
from app.users.models import User
from app.users.forms import RegisterForm, LoginForm, AccountForm

from app.token import generate_confirmation_token, confirm_token
from app.email import send_email

from app.oauth import OAuthSignIn

from config import DATABASE_QUERY_TIMEOUT

mod = Blueprint('users', __name__, url_prefix='/users')

# check for slow quieries
@mod.after_request
def after_request(response):
	for query in get_debug_queries():
		if query.duration >= DATABASE_QUERY_TIMEOUT:
			app.logger.warning(
				"SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" %
				(query.statement, query.parameters, query.duration, query.context)
			)
	return response

# Login
@mod.route('/login/', methods=['GET','POST'])
def login():
	"""Handels user login"""

	if current_user.is_authenticated():
		flash('You are logged in', 'info')
		return redirect(url_for('simple_page.index'))

	# if login form is submitted
	form = LoginForm(request.form)

	if request.method == 'GET':
		return render_template('users/login.html', form=form)

	# verify the login form
	if form.validate_on_submit():
		registered_user = User.query.filter_by(username=form.username.data).first()

		if (registered_user is not None) and check_password_hash(registered_user.password, form.password.data):
			# login user to system
			login_user(registered_user, remember=form.remember_me.data)

			flash('Logged in successfully', 'success')
			return redirect(request.args.get('next') or url_for('simple_page.index'))

		flash('Wrong username or password', 'error')

	return render_template('users/login.html', form=form)

# Register
@mod.route('/register/', methods=['GET','POST'])
def register():
	"""Provides registering for user"""

	# if register form is submitted
	form = RegisterForm(request.form)

	# verify the register form
	if form.validate_on_submit():
		# check if user with provided name or email exists
		check_user = User.query.filter(
			(User.username == form.username.data) |
			(User.email == form.email.data)
		).first()

		# user with username exists
		if check_user is not None:
			flash('User with provided username or email arleady exists', 'error')
			return render_template('users/register.html', form=form)

		# create user and add to database
		user = User(
			username=form.username.data,
			password=generate_password_hash(form.password.data),
			email=form.email.data
		)
		db.session.add(user)
		db.session.commit()

		# sending email
		token = generate_confirmation_token(user.email)
		confirm_url = url_for('users.confirm_email', token=token, _external=True)
		html = render_template('users/activate.html', confirm_url=confirm_url)
		subject = "Please confirm your email"
		send_email(user.email, subject, html)

		#login_user(user)

		# everything okay so far
		flash('A confirmation email has been sent via email.', 'info')
		flash('User successfully registered', 'success')
		return redirect(url_for('users.login'))

	return render_template('users/register.html', form=form)

# Logout
@mod.route('/logout/')
@login_required
def logout():
	"""Logout user from the system"""

	# logout user from system
	logout_user()

	# everything okay so back
	flash('Logged out successfully', 'success')
	return redirect(url_for('simple_page.index'))

@mod.route('/account/', methods=['GET','POST'])
@login_required
def account():
	"""Show users informations"""

	# get form
	form = AccountForm(request.form, obj=g.user)

	# verify the register form
	if form.validate_on_submit():
		if (form.old_password.data is not None) and (form.old_password.data is not '') and (not check_password_hash(g.user.password, form.old_password.data)):
			# everything is okay
			flash('Old password is not correct', 'error')
			return redirect(url_for('users.account'))

		# update user
		form.populate_obj(g.user)

		# add/update user to database
		db.session.commit()

		# everything is okay
		flash('You acccount has been successfully edited', 'success')
		return redirect(url_for('users.account'))

	return render_template('users/account.html', form=form)

@mod.route('/authorize/<provider>')
def oauth_authorize(provider):
	if not g.user.is_anonymous():
		return redirect(url_for('simple_page.index'))

	oauth = OAuthSignIn.get_provider(provider)
	return oauth.authorize()


@mod.route('/callback/<provider>')
def oauth_callback(provider):
	if not g.user.is_anonymous():
		return redirect(url_for('simple_page.index'))

	oauth = OAuthSignIn.get_provider(provider)
	social_id, username, email = oauth.callback()
	if social_id is None:
		flash('Authentication failed', 'error')
		return redirect(url_for('simple_page.index'))

	# check if user exists and if no creates new
	user = User.query.filter_by(social_id=social_id).first()
	if user is None:
		user = User(username=username, password='', email=email, social_id=social_id)
		db.session.add(user)
		db.session.commit()

	login_user(user, True)
	return redirect(url_for('simple_page.index'))

@mod.route('/confirm/<token>')
@login_required
def confirm_email(token):
	try:
		email = confirm_token(token)
	except:
		flash('The confirmation link is invalid or has expired', 'warning')

	# check if user with decoded email exists
	user = User.query.filter_by(email=email).first_or_404()
	if user.confirmed:
		flash('Account already confirmed. Please login', 'info')
	else:
		# update user informations and add to database
		user.confirmed = True
		user.confirmed_on = datetime.datetime.now()
		db.session.add(user)
		db.session.commit()

		flash('You have confirmed your account. Thanks', 'success')

	return redirect(url_for('simple_page.index'))
