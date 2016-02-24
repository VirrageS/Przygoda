#!/bin/bash

command_exists () {
    type "$1" &> /dev/null;
}

# stop redis
if command_exists apt-get; then
    sudo apt-get install redis-tools
    sudo redis-cli shutdown
fi

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
