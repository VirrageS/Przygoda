# Przygoda
Aplikacja Przygoda jest najlepszym sposobem na znajdowanie miłośników rowerów

# Installation

## Clone GitHub project
Note that my current folder is `Desktop` (your path can differ)

	MacBook-Air-Janusz:Desktop VirrageS$
	MacBook-Air-Janusz:Desktop VirrageS$ git clone https://github.com/VirrageS/Przygoda
	MacBook-Air-Janusz:Desktop VirrageS$ cd Przygoda
	MacBook-Air-Janusz:Przygoda VirrageS$

## Initialize virtualenv and install dependencies
Now we are installing virtual env to make app work.

To install virtual env (pick one which will be working :P):

	MacBook-Air-Janusz:Przygoda VirrageS$ sudo pip install virtualenv

or:

	MacBook-Air-Janusz:Przygoda VirrageS$ sudo easy_install virtualenv

Now install dependencies for project

	MacBook-Air-Janusz:Przygoda VirrageS$ virtualenv flaskenv
	MacBook-Air-Janusz:Przygoda VirrageS$ source flaskenv/bin/activate
	(flaskenv)MacBook-Air-Janusz:Przygoda VirrageS$ pip install -r requirements.txt

## Create database
Creating database which will be used by app. Note that everytime you do this old database is deleted!!

	MacBook-Air-Janusz:Przygoda VirrageS$
	MacBook-Air-Janusz:Przygoda VirrageS$ source flaskenv/bin/activate
	(flaskenv)MacBook-Air-Janusz:Przygoda VirrageS$ python shell.py
	>>> from app import db
	>>> db.create_all()
	>>> exit()

(You should do it only when launching app for the first time, added new module which requires new table or modified existing one).

## Run
Note that if your are not in virtual env you should type:

	MacBook-Air-Janusz:Przygoda VirrageS$
	MacBook-Air-Janusz:Przygoda VirrageS$ source flaskenv/bin/activate
	(flaskenv)MacBook-Air-Janusz:Przygoda VirrageS$

Now you can easily run your app `python run.py`.

	(flaskenv)MacBook-Air-Janusz:Przygoda VirrageS$ python run.py
	 * Running on http://127.0.0.1:5000/
	 * Restarting with reloader

Open your web-browser at [http://127.0.0.1:5000], you should be redirected to the website
