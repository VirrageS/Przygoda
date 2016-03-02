# Przygoda | [![Circle CI](https://circleci.com/gh/VirrageS/przygoda.svg?style=shield&&circle-token=bbdd9a0c1379c15241b877d9678c64538730b6d5)](https://circleci.com/gh/VirrageS/przygoda) | [![Build Status](https://travis-ci.org/VirrageS/przygoda.svg?branch=master)](https://travis-ci.org/VirrageS/przygoda) | [![Coverage Status](https://coveralls.io/repos/github/VirrageS/przygoda/badge.svg?branch=master)](https://coveralls.io/github/VirrageS/przygoda?branch=master)

The best way to find enthusiasts of bike tours.

Application make it easier to connect and create bike rides.

## Live website

[Bike Adventures](http://www.sportoweprzygody.pl)

## About

Application is build on microframework [Flask](https://github.com/mitsuhiko/flask).

## Preinstall

### Clone GitHub project

Our first move is to clone GitHub project into our computer.

	$ sudo apt-get install git
	$ git clone https://github.com/VirrageS/przygoda
	$ cd przygoda

### Virtual Environment initialization

Now we have to install virtual env and get all python packages we need.
So lets get python packages first:

	przygoda$ sudo apt-get update
	przygoda$ sudo apt-get install python3-pip python3-dev
	przygoda$ sudo apt-get build-dep python3-psycopg2

Now we need to install virtual env:

	przygoda$ sudo pip3 install virtualenv

Lets create virtual env in our folder:

	przygoda$ virtualenv env

Now we have to start our virtual env (if ever would want to leave virtual env just type `deactivate`):

	przygoda$ source env/bin/activate

And finally install requirements which we need to make our app running.
This code will install all dependencies which our app is using. You can open `requirements.txt` to see what they are.

	(env)przygoda$ pip3 install -r requirements.txt

### Database

Now we have to create simply database which will handle our queries.
To make one, type:

	(env)przygoda$ python3 shell.py
	>>> db.create_all()
	>>> exit()

**IMPORTANT**: you have to be in virtual environment

Unfortunetly if we use sqlite database we need delete our database and
create fresh one every time we code new model or add something to existing one.

### Run app

Now we can run our app by just typing `python3 run.py`.

    przygoda$ ./run-redis; ./run-celery
    przygoda$ . ./env/bin/activate
	(env)przygoda$ python3 run.py
	 * Running on http://127.0.0.1:5000/
	 * Restarting with reloader

**IMPORTANT**: you have to be in virtual environment

Hurray! Our app is alive. Open [http://127.0.0.1:5000] in your browser and that's it!

## Testing

To run unit tests type:

	(env)przygoda$ nosetests --with-coverage --cover-erase --cover-package=app --cover-html

## Babel

To run babel

	(env)przygoda$ pybabel extract -F babel.cfg -o messages.pot app
	(env)przygoda$ pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot app
	(env)przygoda$ pybabel init -i messages.pot -d app/translations -l pl
	(env)przygoda$ pybabel compile -d app/translations

to update

	(env)przygoda$ pybabel extract -F babel.cfg -o messages.pot app
	(env)przygoda$ pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot app
	(env)przygoda$ pybabel update -i messages.pot -d app/translations
	(env)przygoda$ pybabel compile -d app/translations

## Stress tests

To check if our site is able to handle a lot of traffic we can preform stress tests:

	ab -k -r -n 50000 -c 500 http://..../

Parameter | Desc | Value
--- | --- | ---
-n | Set how much packets will be send to our server | 50000
-c | Simulate simultaneous user connections (most important parameter) | 500

---

## Extras

### Gunicorn

Now we have to create script that will run our server. First step is to type:

	sudo nano /etc/init/przygoda.conf

and put this code:

```
description \"Gunicorn application server running PROJECT_NAME\"

start on runlevel [2345]
stop on runlevel [!2345]

respawn
setuid USER
setgid www-data

env PATH=/home/USER/PROJECT_NAME/env/bin
env CONFIG=Development

env MAIL_USERNAME=CHANGE_THIS_!!!
env MAIL_PASSWORD=CHANGE_THIS_!!!
env DATABASE_USERNAME=CHANGE_THIS_!!!
env DATABASE_PASSWORD=CHANGE_THIS_!!!
env DATABASE_HOST=CHANGE_THIS_!!!
env DATABASE_PORT=CHANGE_THIS_!!!
env DATABASE_NAME=CHANGE_THIS_!!!
env CREDENTIALS_FB_ID=CHANGE_THIS_!!!
env CREDENTIALS_FB_SECRET=CHANGE_THIS_!!!
env API_KEY=CHANGE_THIS_!!!

chdir /home/USER/PROJECT_NAME
exec gunicorn --workers 3 --bind unix:PROJECT_NAME.sock -m 007 run:app
```

Before saving. Change **USER** and **PROJECT_NAME** to our current user and project name
for example: `ubuntu` and `przygoda` respectively.
Now lets test our script and set it running.

	sudo start przygoda

### NGINX

First step is to remove default sites because we will not need them. Type:

	sudo rm -rf /etc/nginx/sites-enabled/default
	sudo rm -rf /etc/nginx/sites-available/default

Create new site by:

	sudo nano /etc/nginx/sites-available/PROJECT_NAME

and put code like this:

```
server {
    listen 80;
    server_name SERVER_IP_ADDRESS;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/USER/PROJECT_NAME/PROJECT_NAME.sock;
        proxy_connect_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

Now we have to connect our site to enabled sites. Type:

	sudo ln -s /etc/nginx/sites-available/PROJECT_NAME /etc/nginx/sites-enabled

Check if our nginx configuration is properly set:

	sudo nginx -t

And start nginx:

	sudo service nginx restart

Now, if we type **SERVER_IP_ADDRESS** into our browser we should see our app up and running :)!
