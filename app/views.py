from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from werkzeug import check_password_hash, generate_password_hash
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required

from app.adventures.models import Adventure

mod = Blueprint('simple_page', __name__, template_folder='templates')

# Index - main path
@mod.route("/")
def index():
	return render_template('index.html', adventures=Adventure.query.order_by(Adventure.date.desc()).all())

# About us
@mod.route("/about")
def about():
	return render_template('about.html')

# Contact
@mod.route("/contact")
def contact():
	return render_template('contact.html')

# How it works
@mod.route("/how-it-works")
def how_it_works():
	return render_template('how-it-works.html')

# Features in our app
@mod.route("/features")
def features():
	return render_template('features.html')

# Carrers - aviable
@mod.route("/carrers")
def carrers():
	return render_template('carrers.html')

# Support
@mod.route("/help")
def help():
	return render_template('help.html')
