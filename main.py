import sqlalchemy
from flask import Flask, Response, request, render_template, url_for, redirect

app = Flask(__name__)
app.debug = True

@app.route("/")
def layout():
    return render_template('layout.html')

@app.route("/awesome")
def awesome():
	return render_template('awesome.html')

if __name__ == "__main__":
    app.run()
