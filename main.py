from flask_sqlalchemy import SQLAlchemy
from flask import Flask, Response, request, render_template, url_for, redirect

from flask.ext.login import LoginManager

# App setup
app = Flask(__name__)

# Database setup
db = SQLAlchemy(app)

# Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Main path - layout
@app.route("/")
def layout():
    return render_template('index.html')

# Something
@app.route("/awesome")
def awesome():
	return render_template('awesome.html')

# Register
@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    user = User(request.form['username'] , request.form['password'],request.form['email'])
    db.session.add(user)
    db.session.commit()
    flash('User successfully registered')
    return redirect(url_for('login'))

# Login
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.debug = True
    app.run()
