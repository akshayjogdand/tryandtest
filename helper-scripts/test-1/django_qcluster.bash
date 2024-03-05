#!/bin/bash

DJANGO_SETTINGS_MODULE=sportappsite.test_settings        
DJANGODIR=/home/www/sports-app/sportappsite/

# Activate the virtual environment
cd $DJANGODIR
source ../bin/activate

exec ./manage.py qcluster
