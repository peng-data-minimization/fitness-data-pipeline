#!/usr/bin/env bash

set -e

pkill -f 'kubectl port-forward.*7778' || true
pkill -f 'kubectl port-forward.*9200' || true
pkill -f 'kubectl port-forward.*5601' || true

helm uninstall dm-pipeline-spi

kubectl exec -c cp-kafka-broker -it dm-pipeline-cp-kafka-0 -- /bin/bash /usr/bin/kafka-topics --delete --zookeeper dm-pipeline-cp-zookeeper:2181 --topic anon
kubectl exec -c cp-kafka-broker -it dm-pipeline-cp-kafka-0 -- /bin/bash /usr/bin/kafka-topics --delete --zookeeper dm-pipeline-cp-zookeeper:2181 --topic deidentified
kubectl exec -c cp-kafka-broker -it dm-pipeline-cp-kafka-0 -- /bin/bash /usr/bin/kafka-topics --delete --zookeeper dm-pipeline-cp-zookeeper:2181 --topic processed