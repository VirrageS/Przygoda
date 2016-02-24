#!/bin/bash

PROJECT_NAME=przygoda
USER=ubuntu

cd /home/$USER/$PROJECT_NAME;

# run redis
. ./run-redis.sh -y;

sleep 5;

# celery requires to save files into folder
cd ..;
sudo chmod -R 777 przygoda/
cd przygoda/;

# run celery
. ./run-celery.sh;

sleep 5;

# start app
sudo start przygoda;
sudo service nginx restart;
