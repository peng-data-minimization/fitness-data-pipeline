#!/usr/bin/env bash

set -e

echo -e "\e[32m\nStopping all kubectl port-forwarding...\e[0m"
pkill -f 'kubectl port-forward.*7778' || true
pkill -f 'kubectl port-forward.*9200' || true
pkill -f 'kubectl port-forward.*5601' || true


echo -e "\e[32m\nGenerating test activity data...\e[0m"
kubectl port-forward deployment/kafka-fitness-data-producer 7778 > /dev/null &
sleep 1
curl -X GET http://localhost:7778/generate-data/start


echo -e "\e[32m\nChecking that data can be consumed...\e[0m"
kubectl exec -c cp-kafka-broker -it dm-pipeline-cp-kafka-0 -- /bin/bash /usr/bin/kafka-console-consumer --bootstrap-server localhost:9092 --topic anon --from-beginning --max-messages 1


echo -e "\e[32m\nChecking that Elasticsearch connector sink works...\e[0m"
kubectl logs dm-pipeline-0 | grep "Delivered" | tail -n 10


echo -e "\e[32m\nQuerying Elasticsearch...\e[0m"
kubectl port-forward service/dm-pipeline-elasticsearch-client 9200 > /dev/null &
sleep 1
curl -s -X GET http://localhost:9200/activities/_search?size=10\&q=*:* | jq .[] | head -n 25


echo -e "\e[32m\nChecking Kibana...\e[0m"
kubectl port-forward deployment/dm-pipeline-kibana 5601 > /dev/null &
sleep 1
open http://localhost:5601


echo -e "\e[32m\nStopping kubectl port-forwarding...\e[0m"
pkill -f 'kubectl port-forward.*7778' || true
pkill -f 'kubectl port-forward.*9200' || true