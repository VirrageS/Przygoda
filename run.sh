#!/bin/bash

# before using this script use
# sudo apt-get git;
# git clone https://github.com/VirrageS/przygoda;

WORKERS=3
PROJECT_NAME=przygoda
USER=ubuntu

apt-get update;
apt-get build-dep python3-psycopg2;
apt-get install python3-pip python3-dev nginx;
pip3 install virtualenv;
cd $PROJECT_NAME;
virtualenv env;
source env/bin/activate;
pip3 install psycopg2;
pip3 install -r requirements.txt;
deactivate;

touch "/etc/init/$PROJECT_NAME.conf";
"
description \"Gunicorn application server running $PROJECT_NAME\"

start on runlevel [2345]
stop on runlevel [!2345]

respawn
setuid $USER
setgid www-data

env PATH=/home/$USER/$PROJECT_NAME/env/bin
chdir /home/$USER/$PROJECT_NAME
exec gunicorn --workers $WORKERS --bind unix:$PROJECT_NAME.sock -m 007 run:app
" > "/etc/init/$PROJECT_NAME.conf";

start $PROJECT_NAME;
rm -rf /etc/nginx/sites-enabled/default;
rm -rf /etc/nginx/sites-available/default;

touch "/etc/nginx/sites-available/$PROJECT_NAME";
"
server {
    listen 80;
    server_name ;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/przygoda/przygoda.sock;
        proxy_connect_timeout 30s;
        proxy_read_timeout 30s;
    }
}
" > "/etc/nginx/sites-available/$PROJECT_NAME";

ln -s /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled;
nginx -t;
service nginx restart;
