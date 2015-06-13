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
	user = User(request.form['username'] , request.form['password'], request.form['email'])
	db.session.add(user)
	db.session.commit()
	flash('User successfully registered')
	return redirect(url_for('users.login'))

# Login
@mod.route('/login/', methods=['GET','POST'])
def login():
	if request.method == 'GET':
		return render_template('users/login.html')

	username = request.form['username']
	password = request.form['password']
	remember_me = False
	if 'remember_me' in request.form:
		remember_me = True
	registered_user = User.query.filter_by(username=username,password=password).first()
	if registered_user is None:
		flash('Username or Password is invalid' , 'error')
		return redirect(url_for('users.login'))
	login_user(registered_user, remember = remember_me)
	flash('Logged in successfully')
	return redirect(request.args.get('next') or url_for('index.index'))

# Logout
@mod.route('/logout/')
def logout():
	logout_user()
	return redirect(url_for('index.index'))
