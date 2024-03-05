#! /bin/bash

mkdir -p /home/www/pid-stats-data

cd /home/www/pid-stats-data

fname="pstree-stats-$(date -u +'%d-%m-%Y-%H-%M-%Z').data"

pstree -Aalpt > "/home/www/pid-stats-data/$fname"

gzip "$fname"
