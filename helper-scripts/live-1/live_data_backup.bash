#/bin/bash

fname="cricket-data-$(date +'%d-%m-%Y-%H-%M-%Z').sql"

pg_dump  -U pg_cricket -d cricket -h localhost -O --clean --create --file="$fname"

tar -cvjf "$fname.tbz2" "$fname"
cp -v  "$fname.tbz2" /tmp
mv  "$fname.tbz2" ../tmp
rm "$fname"
ls -lh "../tmp/$fname.tbz2"
