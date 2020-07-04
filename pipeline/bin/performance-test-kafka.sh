#!/usr/bin/env bash

set -eo pipefail

echo -e "\e[32m\nDownloading Kafka client manifest...\e[0m"
curl -O https://raw.githubusercontent.com/confluentinc/cp-helm-charts/master/examples/kafka-client.yaml 2> /dev/null && echo -e "\e[32mVSuccessfully downloaded kafka-client.yaml.\e[0m"

echo -e "\e[32m\nDeploying Kafka client pod...\e[0m"
kubectl apply -f kafka-client.yaml

kubectl exec -it kafka-client -- /bin/bash << EOF

# Show Topics
echo -e "\e[32m\nGetting topics from Zookeeper...\e[0m"
kafka-topics --zookeeper dm-pipeline-cp-zookeeper:2181 --list

# Update Internal Topics (Workaround for https://github.com/confluentinc/schema-registry/issues/698)
echo -e "\e[32m\nMonkey patching Schema-Registry issue #698...\e[0m"
kafka-topics --zookeeper dm-pipeline-cp-zookeeper:2181 --alter --topic _schemas --config cleanup.policy=compact

# Create Topic
echo -e "\e[32m\nCreating topic...\e[0m"
kafka-topics --zookeeper dm-pipeline-cp-zookeeper:2181 --create --topic test --partitions 6 --replication-factor 1
kafka-topics --zookeeper dm-pipeline-cp-zookeeper:2181 --describe -topic test

# Producer
echo -e "\e[32m\nProducing records...\e[0m"
kafka-run-class org.apache.kafka.tools.ProducerPerformance --topic test --print-metrics --num-records 6000000 --throughput 100000 --payload-file /example-activity.json --producer-props bootstrap.servers=dm-pipeline-cp-kafka-headless:9092 buffer.memory=67108864 batch.size=8196

# Consumer
echo -e "\e[32m\nConsuming records...\e[0m"
kafka-consumer-perf-test --broker-list dm-pipeline-cp-kafka-headless:9092 --topic test --print-metrics --messages 6000000 --threads 1
EOF