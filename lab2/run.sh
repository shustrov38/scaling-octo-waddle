#!/bin/bash

DATASET_PATH="hdfs://namenode:9000/Synthetic_Financial_datasets_log.csv"
SPARK_CMD="docker exec -it spark-master spark-submit --master spark://spark-master:7077"

NUM_EXPS=4




docker-compose -f docker-compose.yml up -d
docker cp -L src/. spark-master:/opt/bitnami/spark/
sleep 40
./entrypoint.sh

for i in `seq 0 $NUM_EXPS`; do
    $SPARK_CMD main.py -d $DATASET_PATH | tail -n 6 >> one_node.txt
done

for i in `seq 0 $NUM_EXPS`; do
    $SPARK_CMD main.py -d $DATASET_PATH -o | tail -n 6 >> one_node_opt.txt
done

docker-compose stop



docker-compose -f docker-compose-3d.yml up -d
docker cp -L src/. spark-master:/opt/bitnami/spark/
sleep 40
./entrypoint.sh

for i in `seq 0 $NUM_EXPS`; do
    $SPARK_CMD main.py -d $DATASET_PATH | tail -n 6 >> three_node.txt
done

for i in `seq 0 $NUM_EXPS`; do
    $SPARK_CMD main.py -d $DATASET_PATH -o | tail -n 6 >> three_node_opt.txt
done

docker-compose stop
