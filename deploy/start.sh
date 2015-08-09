#!/bin/bash

PROJECT_NAME=przygoda
USER=ubuntu

cd /home/$USER/$PROJECT_NAME;

# run redis
sudo ./run-redis.sh
sudo ./run-celery.sh

sleep 60

# start app
sudo start przygoda;
sudo service nginx restart;
