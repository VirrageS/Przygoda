#!/bin/bash

PROJECT_NAME=przygoda
USER=ubuntu

# stop all node services
sudo stop przygoda;
sudo service nginx stop;

# remove all client/server files
sudo rm -f /etc/init/$PROJECT_NAME.conf
sudo rm -rf /etc/init/$PROJECT_NAME.conf

sudo rm -f /etc/nginx/sites-enabled/$PROJECT_NAME;
sudo rm -f /etc/nginx/sites-available/$PROJECT_NAME;
sudo rm -rf /etc/nginx/sites-enabled/$PROJECT_NAME;
sudo rm -rf /etc/nginx/sites-available/$PROJECT_NAME;

sudo rm -rf /home/$USER/$PROJECT_NAME

# make fresh directories
sudo mkdir /home/$USER/$PROJECT_NAME

sudo find /home/$USER/$PROJECT_NAME -type d -exec chmod 777 {} \;
sudo find /home/$USER/$PROJECT_NAME -type f -exec chmod 644 {} \;


sudo mkdir /home/$USER/$PROJECT_NAME/logs
sudo chmod 755 /logs
