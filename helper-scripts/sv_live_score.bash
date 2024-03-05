#!/bin/bash

source /Users/svithlani/src/sports-app-cached/bin/activate

echo "Match id=$1, Match key=$2, Interval=$3, Redo=$4"
echo "Kicking off in 5 seconds...."

sleep 5

export DJANGO_SETTINGS_MODULE='sportappsite.settings_cached'
cd /Users/svithlani/src/sports-app-cached/sportappsite/

echo "Season Details $(date)"
./manage.py season_details iplt20_2018

echo "Match Details $(date)"
./manage.py match_details iplt20_2018_"$2"

echo "Ball by Ball $(date)"
./manage.py ball_by_ball iplt20_2018_"$2" -interval "$3" "$4"

echo "Match Completion $(date)"
./manage.py match_completion iplt20_2018_"$2"

echo "Player Scoring $(date)"
./manage.py score_match --match-id="$1" --re-score --no-print

echo "Prediction Scoring  $(date)"
./manage.py score_member_predictions --match-id="$1"
