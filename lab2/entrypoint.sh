#!/bin/bash

FILE="Synthetic_Financial_datasets_log.csv"

docker exec -it namenode hdfs dfsadmin -safemode leave

docker cp data/$FILE namenode:/

docker exec -it namenode bash -c "(hdfs dfs -test -e /$FILE) || (hdfs dfs -put /$FILE /)"