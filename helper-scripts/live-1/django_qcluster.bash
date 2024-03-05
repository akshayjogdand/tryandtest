#!/bin/bash

DJANGODIR=/home/www/sports-app/sportappsite/
VENV=/home/www/sports-app-virtualenv

# Activate the virtual environment
source $VENV/bin/activate

export DJANGO_SETTINGS_MODULE=sportappsite.production_settings        

cd $DJANGODIR
exec ./manage.py qcluster
