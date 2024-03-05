#!/bin/bash

demand_file='/tmp/i-kn-hz-data-plz'

while true; do
    sleep 10

    if [[ -e "$demand_file" ]]; then

	fname=$(cat "$demand_file")
	zipped_fname="$fname.tbz2"

	echo "======="	
        echo "$(date -u)"
	echo "Generating $fname"

	pg_dump  -U cricket_user -d cricket -h localhost -O --clean --create --file="$fname"
	tar -cvjf "$zipped_fname" "$fname" /home/www/sports-app/sportappsite/static/media
	find /tmp -maxdepth 1  -name '*.tbz2' -delete -print
	find ../tmp -maxdepth 1 -name '*.tbz2' -delete -print
	cp -v  "$zipped_fname" /tmp
	mv  "$zipped_fname" ../tmp
	rm "$fname"

	echo "All done."
	echo "$(date -u)"
	echo "======="

	# Allow remote client extra time to finish and cleanup demand file.
	sleep 300

    fi
done
