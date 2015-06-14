from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from werkzeug import check_password_hash, generate_password_hash
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required

from app import db
from app.users.models import User

mod = Blueprint('users', __name__, url_prefix='/users')

# Register
@mod.route('/register/' , methods=['GET','POST'])
def register():
	if request.method == 'GET':
		return render_template('users/register.html')

	# @todo: check if request forms are filled properly
	# @todo: check if user exists in database

	# create new user
	user = User(
		request.form['username'],
		request.form['password'],
		request.form['email']
	)
	# add user to database
	db.session.add(user)
	db.session.commit()

	# everything okay so back
	flash('User successfully registered')
	return redirect(url_for('users.login'))

# Login
@mod.route('/login/', methods=['GET','POST'])
def login():
	"""Handels login path"""

	if request.method == 'GET':
		return render_template('users/login.html')

	# get username and password from text fields in form
	username = request.form['username']
	password = request.form['password']

	# remember me - must be in form
	remember_me = False
	if 'remember_me' in request.form:
		remember_me = True

	# get user from database
	registered_user = User.query.filter_by(
		username=username,
		password=password
	).first()

	# failed to get user
	if registered_user is None:
		flash('Username or Password is invalid' , 'error')
		return redirect(url_for('users.login'))

	# login user to system
	login_user(registered_user, remember=remember_me)

	# everything okay so back
	flash('Logged in successfully')
	return redirect(request.args.get('next') or url_for('simple_page.index'))

# Logout
@mod.route('/logout/')
def logout():
	"""Handels logout path"""

	# logout user from system
	logout_user()

	# everything okay so back
	flash('Logged out successfully')
	return redirect(url_for('simple_page.index'))
