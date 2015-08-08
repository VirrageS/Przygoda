#!/bin/bash

# run redis
sudo ./run-redis.sh

# start celery
. ./env/bin/activate;
celery worker -A app.celery --loglevel=info
deactivate;

# start app
sudo start przygoda;
sudo service nginx restart;
