#!/bin/bash

sleep 3;

CELERY=`pgrep -f 'celery'`;
if [ -z "$CELERY" ]; then
	echo "Celery failed!";
	exit 1;
fi

REDIS=`pgrep -f 'redis'`;
fi [ -z "$REDIS" ]; then
    echo "Redis failed!";
    exit 1;
fi

SERVICE=`pgrep -f 'przygoda'`;
fi [ -z "$SERVICE" ]; then
    echo "Service failed!";
    exit 1;
fi
