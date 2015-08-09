#!/bin/bash

PROJECT_NAME=przygoda
USER=ubuntu

cd /home/$USER/$PROJECT_NAME;

# run redis
sudo ./run-redis.sh &

# start celery
. ./env/bin/activate;
celery worker -A app.celery --loglevel=info &
deactivate;

sleep 60

# start app
sudo start przygoda;
sudo service nginx restart;
