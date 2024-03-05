#!/bin/bash

log(){
    echo $(date -u)
    echo "    $1"
}

demand_file='/tmp/deploy-test-1'

export DJANGO_SETTINGS_MODULE='sportappsite.test_settings'

source /home/www/sports-app/bin/activate

while true; do
    sleep 10

    if [[ -e "$demand_file" ]]; then

	log "Demand file found."

	supervisorctl -c /home/www/sports-app/helper-scripts/test-1/supervisord.conf stop sportappsite sportappsite-django-q
	log "Supervisor stopped."

	mkdir -p /tmp/deploys
	cd /tmp/deploys/
	rm -rf *
	tar xvjf /data-backups/latest-data
	sql_file=$(ls *.sql)
	log "Loading: $sql_file"
	psql -U cricket_user -h localhost < "$sql_file"
	log "DB Refreshed."

	rsync -zvhr home/www/sports-app/sportappsite/static/media/* /home/www/sports-app/sportappsite/static/media/
	log "Media Synced"
	
	rm -rf *

	log "Installing Py packages via pip"
	pip install -r /home/www/sports-app/py-requirements-test.txt

	cd /home/www/sports-app/sportappsite
	old=$(hg id)
	hg pull -uv
	new=$(hg id)
	log "Updated backend: $old   -->  $new"
	log "Running migrations + Member disabling."
	cd /home/www/sports-app/sportappsite
	./manage.py migrate
	./manage.py disable_members_on_test

	cd /home/www/new-stumpguruweb
	old=$(hg id)
	hg pull -uv
	new=$(hg id)
	log "Updated frontend: $old   -->  $new"
	log "Building frontend."
	yarn build

	supervisorctl -c /home/www/sports-app/helper-scripts/test-1/supervisord.conf start sportappsite sportappsite-django-q
	log "Supervisor started."

	log "Deploy completed."

    fi
done
