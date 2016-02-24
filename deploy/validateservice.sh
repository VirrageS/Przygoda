#!/bin/bash

sleep 3;

CELERY=`pgrep -f 'celery'`;
if [ -z "$CELERY" ]; then
	echo "Celery failed!";
	exit 1;
fi

REDIS=`pgrep -f 'redis'`;
if [ -z "$REDIS" ]; then
    echo "Redis failed!";
    exit 1;
fi

SERVICE=`pgrep -f 'przygoda'`;
if [ -z "$SERVICE" ]; then
    echo "Service failed!";
    exit 1;
fi
