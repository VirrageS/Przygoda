#!/bin/bash

PROJECT_NAME=przygoda
USER=ubuntu

cd /home/$USER/;
sudo chown ubuntu:ubuntu $PROJECT_NAME/;
sudo chmod -R 777 $PROJECT_NAME/;
cd $PROJECT_NAME;

# run redis
. ./run-redis.sh -y;

sleep 5;

# run celery
. ./run-celery.sh;

sleep 5;

# start app
sudo start przygoda;
sudo service nginx restart;
