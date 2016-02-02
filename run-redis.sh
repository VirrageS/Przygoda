#!/bin/bash

if [ ! -d redis-stable/src ]; then
    curl -O http://download.redis.io/redis-stable.tar.gz
    tar xvzf redis-stable.tar.gz
    rm redis-stable.tar.gz
fi

cd redis-stable
make

if [ "$EUID" -ne 0 ]; then
    ./src/redis-server ../redis.conf
else
    sudo ./src/redis-server ../redis.conf
fi

echo "Redis - Ready"
