#!/bin/bash

PROJECT_NAME=przygoda
USER=ubuntu

cd /home/$USER/$PROJECT_NAME;

# run redis
. ./run-redis.sh
. ./run-celery.sh

sleep 60

# start app
sudo start przygoda;
sudo service nginx restart;
