#!/bin/bash

# stop celery
sudo ps auxww | grep 'celery worker' | awk '{print $2}' | xargs kill -9

# start celery
. ./env/bin/activate;
celery multi start 4 --time-limit=300 --concurrency=2 -A app.celery
deactivate;

echo "Celery - Ready"
