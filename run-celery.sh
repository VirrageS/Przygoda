PROJECT_NAME=przygoda
USER=ubuntu

cd /home/$USER/$PROJECT_NAME;

# start celery
. ./env/bin/activate;
celery worker -A app.celery --loglevel=info &
deactivate;
