#!/usr/bin/env bash

set -eo pipefail

# curl -O https://raw.githubusercontent.com/confluentinc/cp-helm-charts/master/examples/kafka-client.yaml
# kubectl apply -f kafka-client.yaml
kubectl exec -it kafka-client -- /bin/bash << EOF

# Setup
export RELEASE_NAME=kafka
export ZOOKEEPERS=${RELEASE_NAME}-cp-zookeeper:2181
export KAFKAS=${RELEASE_NAME}-cp-kafka-headless:9092

# Create Topic
kafka-topics --zookeeper $ZOOKEEPERS --create --topic ingestion --partitions 6 --replication-factor 1
kafka-topics --zookeeper $ZOOKEEPERS --create --topic harmonized --partitions 6 --replication-factor 1
kafka-topics --zookeeper $ZOOKEEPERS --create --topic processed --partitions 6 --replication-factor 1

# Producer
kafka-run-class org.apache.kafka.tools.ProducerPerformance --print-metrics --topic ingestion --num-records 6000000 --throughput 100000 --record-size 100 --producer-props bootstrap.servers=$KAFKAS buffer.memory=67108864 batch.size=8196

# Consumer
kafka-consumer-perf-test --broker-list $KAFKAS --messages 6000000 --threads 1 --topic ingestion --print-metrics

EOF