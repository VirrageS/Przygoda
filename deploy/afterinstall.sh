#!/bin/bash

# before using this script use
# sudo apt-get install git;
# git clone https://github.com/VirrageS/przygoda;

WORKERS=3
PROJECT_NAME=przygoda
USER=ubuntu
IP=przygoda-1532623138.eu-west-1.elb.amazonaws.com

sudo apt-get update;
sudo apt-get build-dep python3-psycopg2;
sudo apt-get install python3-pip python3-dev nginx;

cd /home/$USER/$PROJECT_NAME;

pip3 install virtualenv;
virtualenv env;

. ./env/bin/activate;
pip3 install psycopg2;
pip3 install -r requirements.txt;
deactivate;

sudo touch /etc/init/$PROJECT_NAME.conf;
echo "
description \"Gunicorn application server running $PROJECT_NAME\"

start on runlevel [2345]
stop on runlevel [!2345]

respawn
setuid $USER
setgid www-data

env PATH=/home/$USER/$PROJECT_NAME/env/bin
chdir /home/$USER/$PROJECT_NAME
exec gunicorn --workers $WORKERS --bind unix:$PROJECT_NAME.sock -m 007 run:app
" | sudo tee --append /etc/init/$PROJECT_NAME.conf > /dev/null


sudo rm -rf /etc/nginx/sites-enabled/default;
sudo rm -rf /etc/nginx/sites-available/default;

sudo touch /etc/nginx/sites-available/$PROJECT_NAME;
echo "
server {
    listen 80;
    server_name $IP;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/$USER/$PROJECT_NAME/przygoda.sock;
        proxy_connect_timeout 30s;
        proxy_read_timeout 30s;
    }
}
" | sudo tee --append /etc/nginx/sites-available/$PROJECT_NAME > /dev/null

sudo ln -s /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled;
sudo nginx -t;