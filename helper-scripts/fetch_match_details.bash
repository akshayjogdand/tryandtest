#!/bin/bash

echo "Temporay script/pattern to fetch a bunch of Matches."

echo "Edit and enable as needed -- now exiting"

exit 0

source /home/www/sports-app/bin/activate

echo "Season Details $(date)"
/home/www/sports-app/sportappsite/prod_manage.py season_details iplt20_2018

(( i=1 ))

while (( i <= 15 ))
do
    ((i += 1))
    echo "Match Details $(date)"
    /home/www/sports-app/sportappsite/prod_manage.py match_details iplt20_2018_"$1"
    sleep 120
done
