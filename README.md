# Przygoda
Aplikacja Przygoda jest najlepszym sposobem na znajdowanie miłośników rowerów

# Installation

## Clone GitHub project
	git clone git@github.com:USERNAME/helloflask.git

## Initialize virtualenv and install dependencies
	sudo pip install virtualenv
	cd PATH_TO_FOLDER
	virtualenv flaskenv
	cd flaskenv
	pip install -r requirements.txt

## Start virtual env
source flaskenv/bin/activate

## Create database
	user@Machine:~/Projects/dev$ source flaskenv/bin/activate
	(flaskenv)user@Machine:~/Projects/dev$ python shell.py
	>>> from app import db
	>>> db.create_all()
	>>> exit()

## Run
Now you can easily run your app `python run.py`.

	(flaskenv)user@Machine:~/Projects/dev$ python run.py
	 * Running on http://127.0.0.1:5000/
	 * Restarting with reloader

Open your web-browser at [http://127.0.0.1:5000], you should be redirected to website
