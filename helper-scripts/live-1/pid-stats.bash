#! /bin/bash

mkdir -p /home/www/pid-stats-data

cd /home/www/pid-stats-data

fname="pid-stats-$(date -u +'%d-%m-%Y-%H-%M-%Z').data"

pidstat -p ALL -rud -h 5 6 > "/home/www/pid-stats-data/$fname"

gzip "$fname"
