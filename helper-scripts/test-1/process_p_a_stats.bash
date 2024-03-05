#!/bin/bash

DJANGODIR=/home/www/sports-app/sportappsite              # Django Project Directory
DJANGO_SETTINGS_MODULE=sportappsite.test_settings        # change 'sportappsite' with your project name
VENV=/home/www/sports-app-virtualenv

# Activate the virtual environment
source $VENV/bin/activate

cd $DJANGODIR
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

exec ./manage.py process_p_a_stats_forever
