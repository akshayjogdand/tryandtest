#!/bin/bash

NAME="sports-app-site"                                   # Django Project Name
DJANGODIR=/home/www/sports-app/sportappsite              # Django Project Directory
SOCKFILE=/home/www/sports-app/run/gunicorn.sock          # Gunicorn Sock File
USER=www                                                 # Django Project Running under user www
GROUP=www                                                # Django Project Running under group www
NUM_WORKERS=10
DJANGO_SETTINGS_MODULE=sportappsite.production_settings  # change 'sportappsite' with your project name
DJANGO_WSGI_MODULE=sportappsite.wsgi                     # change 'sportappsite' with your project name
VENV=/home/www/sports-app-virtualenv

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
source $VENV/bin/activate

cd $DJANGODIR
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec $VENV/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
--name $NAME \
--workers $NUM_WORKERS \
--user=$USER --group=$GROUP \
--bind=unix:$SOCKFILE \
--log-level=debug \
--log-file=-
