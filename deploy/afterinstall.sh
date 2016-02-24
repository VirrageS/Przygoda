#!/bin/bash

# before using this script use
# sudo apt-get install git;
# git clone https://github.com/VirrageS/przygoda;

WORKERS=4
PROJECT_NAME=przygoda
USER=ubuntu
IP=przygoda-1532623138.eu-west-1.elb.amazonaws.com

sudo apt-get --yes update;
sudo apt-get --yes build-dep python3-psycopg2;
sudo apt-get --yes install python3-pip python3-dev nginx git;

cd /home/$USER/$PROJECT_NAME;

pip3 install virtualenv;
virtualenv env;

. ./env/bin/activate;
pip3 install psycopg2;
pip3 install -r requirements.txt;
pip3 install --upgrade -r requirements.txt;
deactivate;

sudo touch /etc/init/$PROJECT_NAME.conf;
echo "description \"Gunicorn application server running $PROJECT_NAME\"

start on runlevel [2345]
stop on runlevel [!2345]

respawn
setuid $USER
setgid www-data

env PATH=/home/$USER/$PROJECT_NAME/env/bin
env CONFIG=Production
env MAIL_USERNAME=CHANGE_THIS_!!!
env MAIL_PASSWORD=CHANGE_THIS_!!!
env DATABASE_USERNAME=CHANGE_THIS_!!!
env DATABASE_PASSWORD=CHANGE_THIS_!!!
env DATABASE_HOST=CHANGE_THIS_!!!
env DATABASE_PORT=CHANGE_THIS_!!!
env DATABASE_NAME=CHANGE_THIS_!!!
env CREDENTIALS_FB_ID=CHANGE_THIS_!!!
env CREDENTIALS_FB_SECRET=CHANGE_THIS_!!!

env API_KEY=CHANGE_THIS_!!!

chdir /home/$USER/$PROJECT_NAME
exec gunicorn --workers $WORKERS --bind unix:$PROJECT_NAME.sock -m 007 run:app" | sudo tee --append /etc/init/$PROJECT_NAME.conf > /dev/null

aws s3 cp s3://przygoda/config.sh /home/$USER/$PROJECT_NAME/config.sh --region eu-west-1
sudo chmod a+x config.sh
. ./config.sh

sudo rm -rf /etc/nginx/sites-enabled/default;
sudo rm -rf /etc/nginx/sites-available/default;

sudo touch /etc/nginx/sites-available/$PROJECT_NAME;
echo "server {
    listen 80;
    server_name $IP;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/$USER/$PROJECT_NAME/$PROJECT_NAME.sock;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
    }
}" | sudo tee --append /etc/nginx/sites-available/$PROJECT_NAME > /dev/null

sudo ln -s /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled;
sudo nginx -t;

sudo mkdir /home/$USER/$PROJECT_NAME/logs
sudo chmod 777 /home/$USER/$PROJECT_NAME/logs

# update translations
sudo chmod -R 777 /home/$USER/$PROJECT_NAME/app/translations
. ./env/bin/activate;
pybabel compile -d app/translations;
deactivate;

sudo chmod a+x run-redis.sh
sudo chmod a+x run-celery.sh

sudo chown ubuntu:ubuntu *;
sudo chmod -R 777 *;
