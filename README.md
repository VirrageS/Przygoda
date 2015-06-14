# Przygoda
Aplikacja Przygoda jest najlepszym sposobem na znajdowanie miłośników rowerów

# Installation

## Clone GitHub project
Note that my current folder is `Desktop`

	MacBook-Air-Janusz:Desktop VirrageS$
	MacBook-Air-Janusz:Desktop VirrageS$ git clone git@github.com:VirrageS/Przygoda.git
	MacBook-Air-Janusz:Desktop VirrageS$ cd Przygoda
	MacBook-Air-Janusz:Przygoda VirrageS$

## Initialize virtualenv and install dependencies
Now we are installing virtual env to make app work

	MacBook-Air-Janusz:Przygoda VirrageS$ sudo pip install virtualenv
	MacBook-Air-Janusz:Przygoda VirrageS$ virtualenv flaskenv
	MacBook-Air-Janusz:Przygoda VirrageS$ cd flaskenv
	MacBook-Air-Janusz:flaskenv VirrageS$ pip install -r requirements.txt

## Create database
Creating database which will be used in app.
It should be done only one time before first start.

	MacBook-Air-Janusz:Przygoda VirrageS$ source flaskenv/bin/activate
	(flaskenv)MacBook-Air-Janusz:Przygoda VirrageS$ python shell.py
	>>> from app import db
	>>> db.create_all()
	>>> exit()

## Run
Note that if your are not in virtual env you should type:

	MacBook-Air-Janusz:Przygoda VirrageS$ source flaskenv/bin/activate

Now you can easily run your app `python run.py`.

	(flaskenv)MacBook-Air-Janusz:Przygoda VirrageS$ python run.py
	 * Running on http://127.0.0.1:5000/
	 * Restarting with reloader

Open your web-browser at [http://127.0.0.1:5000], you should be redirected to the website
