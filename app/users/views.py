# -*- coding: utf-8 -*-

import datetime
from werkzeug import check_password_hash, generate_password_hash
from flask import Blueprint, request, render_template, flash, redirect, url_for
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

	# user is logged so it does not need to be logged in again
	if current_user.is_authenticated():
		flash('Już jesteś zalogowany', 'info')
		return redirect(url_for('simple_page.index'))

	# get form
	form = LoginForm(request.form)

	if request.method == 'GET':
		return render_template('users/login.html', form=form)

	# verify the login form
	if form.validate_on_submit():
		registered_user = User.query.filter_by(username=form.username.data).first()

		if (registered_user is not None) and check_password_hash(registered_user.password, form.password.data):
			# login user to system
			login_user(registered_user, remember=form.remember_me.data)

			flash(u'Zalogowałeś sie poprawnie. Witaj w Przygodzie.', 'success')
			return redirect(request.args.get('next') or url_for('simple_page.index'))

		flash(u'Nieprawidłowe hasło lub nazwa użytkownika', 'danger')

	return render_template('users/login.html', form=form)

# Register
@mod.route('/register/', methods=['GET', 'POST'])
def register():
	"""Provides registering for user"""

	# if user is logged in it does not need to be registered
	if current_user.is_authenticated():
		flash('You are arleady logged in', 'info')
		return redirect(url_for('simple_page.index'))

	# if register form is submitted
	form = RegisterForm(request.form)

	# verify the register form
	if form.validate_on_submit():
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
		flash('Email potwierdzający został wysłany', 'info')
		flash('Użytkownik został zarejestrowany poprawnie. Witaj w Przygodzie.', 'success')
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
	flash('Wylogowałeś sie z Przygody', 'success')
	return redirect(url_for('simple_page.index'))

@mod.route('/account/', methods=['GET','POST'])
@login_required
def account():
	"""Show users informations"""

	# get form
	form = AccountForm(request.form, obj=current_user)

	# verify the register form
	if form.validate_on_submit():
		if current_user.email is not form.email.data:
			# resending email
			token = generate_confirmation_token(current_user.email)
			confirm_url = url_for('users.confirm_email', token=token, _external=True)
			html = render_template('users/activate.html', confirm_url=confirm_url)
			subject = u"Potwierdź swój email - Przygoda"
			send_email(current_user.email, subject, html)
			flash(u'Email potwierdzający został wysłany', 'info')

		# update user
		form.populate_obj(current_user)

		# update user in database
		db.session.commit()

		# everything is okay
		flash('Your acccount has been successfully edited', 'success')
		return redirect(url_for('users.account'))

	return render_template('users/account.html', form=form)

@mod.route('/authorize/<provider>')
def oauth_authorize(provider):
	if not current_user.is_anonymous():
		return redirect(url_for('simple_page.index'))

	oauth = OAuthSignIn.get_provider(provider)
	return oauth.authorize()


@mod.route('/callback/<provider>')
def oauth_callback(provider):
	if not current_user.is_anonymous():
		return redirect(url_for('simple_page.index'))

	oauth = OAuthSignIn.get_provider(provider)
	social_id, username, email = oauth.callback()
	if social_id is None:
		flash('Authentication failed', 'danger')
		return redirect(url_for('simple_page.index'))

	# check if user exists and if no creates new
	user = User.query.filter_by(social_id=social_id).first()
	if user is None:
		user = User(username=username, password='', email=email, social_id=social_id)
		db.session.add(user)
		db.session.commit()

	login_user(user, remember=True)
	return redirect(url_for('simple_page.index'))

# Send confirmation email
@mod.route('/confirmation/')
@login_required
def resend_confirmation_email():
	# resending email
	token = generate_confirmation_token(current_user.email)
	confirm_url = url_for('users.confirm_email', token=token, _external=True)
	html = render_template('users/activate.html', confirm_url=confirm_url)
	subject = "Please confirm your email"
	send_email(current_user.email, subject, html)

	flash(u'Email potwierdzający został wysłany', 'info')
	return redirect(url_for('simple_page.index'))

# Confirm email
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
		flash('Account already confirmed', 'info')
		return redirect(url_for('simple_page.index'))

	# update user informations and add to database
	user.confirmed = True
	user.confirmed_on = datetime.datetime.now()
	db.session.add(user)
	db.session.commit()

	flash('You have confirmed your account. Thanks', 'success')
	return redirect(url_for('simple_page.index'))
