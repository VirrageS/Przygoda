#!/bin/bash

# stop celery
sudo ps auxww | grep 'celery worker' | awk '{print $2}' | xargs kill -9

# start celery
. ./env/bin/activate;
celery worker -A app.celery --loglevel=info &
deactivate;

echo "Celery - Ready"
