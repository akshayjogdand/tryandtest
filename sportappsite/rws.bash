#! /bin/bash

source /home/www/sports-app-virtualenv/bin/activate
cd /home/www/sports-app/sportappsite

export DJANGO_SETTINGS_MODULE=sportappsite.production_settings

./manage.py match_details wisl_2021_t20_03
./manage.py ball_by_ball wisl_2021_t20_03 -r -interval 1
./manage.py match_completion wisl_2021_t20_03
./manage.py score_match --match-id=965 --re-score --no-print
./manage.py score_member_predictions --match-id=965
./manage.py compute_player_stats --match-id=965 --delete-previous
