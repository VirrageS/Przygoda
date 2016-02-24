#!/bin/bash

# celery requires to save files into folder
cd ..;
sudo chmod 777 przygoda/
cd przygoda/;

# stop celery
sudo ps auxww | grep 'celery worker' | awk '{print $2}' | xargs kill -9

# start celery
. ./env/bin/activate;
celery multi start 4 --time-limit=300 --concurrency=2 -A app.celery --loglevel=info
deactivate;

echo "Celery - Ready"
