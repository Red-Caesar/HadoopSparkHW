#!/bin/bash
NAMENODE_CONTAINER="namenode"

echo "Waiting for HDFS to be ready..."
docker exec $NAMENODE_CONTAINER hdfs dfsadmin -safemode wait
docker exec $NAMENODE_CONTAINER hdfs dfsadmin -report | grep "Live datanodes"

docker exec $NAMENODE_CONTAINER hdfs dfs -mkdir -p /data
docker cp data/spotify_dataset.csv $NAMENODE_CONTAINER:/tmp/
docker exec -it $NAMENODE_CONTAINER hdfs dfs -put /tmp/spotify_dataset.csv /data/
echo "Data uploaded to HDFS: /data/spotify_dataset.csv"