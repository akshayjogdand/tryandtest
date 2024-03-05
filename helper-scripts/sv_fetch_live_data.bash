#! /bin/bash

mkdir -p ../sportappsite/tmp/

demand_file='/tmp/i-kn-hz-data-plz'

fname="cricket-data-$(date -u +'%d-%m-%Y-%H-%M-%Z').sql"

zipped_fname="$fname.tbz2"

ssh fab-prod-1 "echo  $fname > $demand_file"

echo "$(date -u)"
echo 'Demand sent, wait for 300 seconds...'

sleep 300

echo "$(date -u)"

ssh fab-prod-1 "rm $demand_file"

scp fab-prod-1:"/tmp/$zipped_fname" ../sportappsite/tmp/

cd ../sportappsite/tmp/

tar xvjf "$zipped_fname"

pkill -f 'runserver'

pkill -f 'redis-server'

pkill -f 'psql'

pkill -f 'qcluster'

/opt/local/bin/psql13 -U svithlani < "$fname" || /opt/local/lib/postgresql12/bin/psql -U svithlani < "$fname"

query='DELETE from django_q_schedule; DELETE from django_q_ormq; DELETE from django_q_task; \q'

echo
echo 'Removing cached QCluster jobs'

echo "$query" | /opt/local/bin/psql13  -U svithlani  -d cricket || echo "$query" |
        /opt/local/bin/psql13  -U svithlani -d cricket

echo "$query"

cp -rv home/www/sports-app/sportappsite/static/media/* /Users/sawanvithlani/src/sports-app/sportappsite/static/media/

cd ../

# Possibly cached Redis data.
rm dump.rdb

./manage.py changepassword sawan

echo "Done"
