import sqlalchemy
from flask import Flask, Response, request, render_template, url_for, redirect

from flask.ext.login import LoginManager

# App setup
app = Flask(__name__)
app.debug = True

# Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Main path - layout
@app.route("/")
def layout():
    return render_template('layout.html')

# Something
@app.route("/awesome")
def awesome():
	return render_template('awesome.html')

if __name__ == "__main__":
    app.run()
