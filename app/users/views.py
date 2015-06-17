from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from werkzeug import check_password_hash, generate_password_hash
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required

from app import db
from app.users.models import User
from app.users.forms import RegisterForm, LoginForm

mod = Blueprint('users', __name__, url_prefix='/users')

# Register
@mod.route('/register/' , methods=['GET','POST'])
def register():
	if request.method == 'GET':
		return render_template('users/register.html')

	username = request.form['username']
	password = request.form['password']
	email = request.form['email']

	# @todo: check if request forms are filled properly

	# check for error
	error = False

	# username was not provided
	if username is None or (username == ''):
		flash('No username')
		error = True

	# password was not provided
	if password is None or (password == ''):
		flash('No password')
		error = True

	# email was not provided
	if (email is None) or (email == ''):
		flash('No email')
		error = True

	# error occured so we back
	if error:
		return render_template('users/register.html')

	# check if user with name exists
	checkUser = User.query.filter_by(username=username).first()

	# check if users with email exists
	if checkUser is None:
		checkUser = User.query.filter_by(email=email).first()

	# user with username exists
	if checkUser != None:
		flash('User with provided username or email arleady exists')
		return render_template('users/register.html')

	# create new user
	user = User(username, generate_password_hash(password), email)

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

	# If sign in form is submitted
	form = LoginForm(request.form)

	if request.method == 'GET':
		return render_template('users/login.html', form=form)

	# Verify the sign in form
	if form.validate_on_submit():
		registered_user = User.query.filter_by(username=form.username.data).first()

		if registered_user: #and check_password_hash(registered_user.password, form.password.data):
			# login user to system
			login_user(registered_user, remember=form.remember_me.data)

			flash('Logged in successfully')
			return redirect(request.args.get('next') or url_for('simple_page.index'))

		flash('Wrong username or password', 'error-message')



	return render_template('users/login.html', form=form)

# Logout
@mod.route('/logout/')
def logout():
	"""Handels logout path"""

	# logout user from system
	logout_user()

	# everything okay so back
	flash('Logged out successfully')
	return redirect(url_for('simple_page.index'))
