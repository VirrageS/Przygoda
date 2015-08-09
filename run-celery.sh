#!/bin/bash

# start celery
. ./env/bin/activate;
celery worker -A app.celery --loglevel=info &
deactivate;
