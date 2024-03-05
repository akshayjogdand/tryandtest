#!/bin/bash

fname="cricket-data-$(date +'%d-%m-%Y-%H-%M-%Z').sql"

/opt/local/lib/postgresql10/bin/pg_dump -U svithlani --clean --create -O --dbname=cricket --file=../sportappsite/tmp/"$fname"

tar -cvjf ../sportappsite/tmp/"$fname.tbz2" ../sportappsite/tmp/"$fname"

ls -lrth ../sportappsite/tmp/

scp ../sportappsite/tmp/"$fname.tbz2" test-1:/data-backups/
