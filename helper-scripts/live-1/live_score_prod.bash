#!/bin/bash

DJANGO_SETTINGS_MODULE=sportappsite.production_settings        
DJANGODIR=/home/www/sports-app/sportappsite/
VENV=/home/www/sports-app-virtualenv

source $VENV/bin/activate

cd $DJANGODIR

echo "Season key=$1 Match id=$2, Match key=$3"
echo "Kicking off in 10 seconds...."

sleep 10

echo "Season Details $(date)"
./manage.py season_details "$1"

echo "Match Details $(date)"
./manage.py match_details "$3"

echo "Ball by Ball $(date)"
./manage.py ball_by_ball "$3" -interval 3 --redo -i 1
./manage.py ball_by_ball "$3" -interval 3 --redo -i 2

echo "Match Completion $(date)"
./manage.py match_completion "$3"

echo "Player Scoring $(date)"
./manage.py score_match --match-id="$2" --no-print --re-score

echo "Prediction Scoring $(date)"
./manage.py score_member_predictions --match-id="$2"

echo "Compute Player Stats $(date)"
./manage.py compute_player_stats --match-id="$2"

#echo 'Re-adjusting match names'
#./manage.py adjust_wc2019_match_names
