from werkzeug import check_password_hash, generate_password_hash
from flask import Blueprint, request, render_template, g, flash, redirect, url_for
from flask.ext.login import login_user, logout_user, login_required
from flask.ext.sqlalchemy import get_debug_queries

from app import app, db
from app.users.models import User
from app.users.forms import RegisterForm, LoginForm, AccountForm

from config import DATABASE_QUERY_TIMEOUT

mod = Blueprint('users', __name__, url_prefix='/users')

@mod.after_request
def after_request(response):
	for query in get_debug_queries():
		if query.duration >= DATABASE_QUERY_TIMEOUT:
			app.logger.warning(
				"SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" %
				(query.statement, query.parameters, query.duration,
				 query.context)
			)
	return response

# Login
@mod.route('/login/', methods=['GET','POST'])
def login():
	"""Handels user login"""

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

			flash('Logged in successfully')
			return redirect(request.args.get('next') or url_for('simple_page.index'))

		flash('Wrong username or password', 'error-message')

	return render_template('users/login.html', form=form)

# Register
@mod.route('/register/', methods=['GET','POST'])
def register():
	# if register form is submitted
	form = RegisterForm(request.form)

	if request.method == 'GET':
		return render_template('users/register.html', form=form)

	# verify the register form
	if form.validate_on_submit():
		# check if user with name exists
		check_user = User.query.filter_by(username=form.username.data).first()

		# check if users with email exists
		if check_user is None:
			check_user = User.query.filter_by(email=form.email.data).first()

		# user with username exists
		if check_user is not None:
			flash('User with provided username or email arleady exists')
			return render_template('users/register.html', form=form)

		# create user and add to database
		user = User(form.username.data, generate_password_hash(form.password.data), form.email.data)
		db.session.add(user)
		db.session.commit()

		# everything okay so far
		flash('User successfully registered')
		return redirect(url_for('users.login'))

	return render_template('users/register.html', form=form)

# Logout
@mod.route('/logout/')
@login_required
def logout():
	"""Handels logout path"""

	# logout user from system
	logout_user()

	# everything okay so back
	flash('Logged out successfully')
	return redirect(url_for('simple_page.index'))

@mod.route('/account/', methods=['GET','POST'])
@login_required
def account():
	# get form
	form = AccountForm(request.form, obj=g.user)

	# verify the register form
	if form.validate_on_submit():
		if (form.old_password.data is not None) and (form.old_password.data is not '') and (not check_password_hash(g.user.password, form.old_password.data)):
			# everything is okay
			flash('Old password is not correct')
			return redirect(url_for('users.account'))

		# get edited user from the form
		form.populate_obj(g.user)

		# add/update user to database
		db.session.commit()

		# everything is okay
		flash('You acccount has been successfully edited')
		return redirect(url_for('users.account'))

	return render_template('users/account.html', form=form)
