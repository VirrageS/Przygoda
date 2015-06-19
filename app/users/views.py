from werkzeug import check_password_hash, generate_password_hash
from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask.ext.login import login_user, logout_user, login_required

from app import db
from app.users.models import User
from app.users.forms import RegisterForm, LoginForm

mod = Blueprint('users', __name__, url_prefix='/users')

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

		if registered_user and check_password_hash(registered_user.password, form.password.data):
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
			flash('User with provided username or email arleady exists', 'error-message')
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

@mod.route('/account/')
@login_required
def account():
	return render_template('users/account.html')
