#!/bin/bash

PROJECT_NAME=przygoda
USER=ubuntu

cd /home/$USER/$PROJECT_NAME;

# run redis
. ./run-redis.sh;

sleep 10;

# run celery
. ./run-celery.sh;

# start app
sudo start przygoda;
sudo service nginx restart;
