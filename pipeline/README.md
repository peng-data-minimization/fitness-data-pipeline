# Streaming Pipeline

A Kubernetes based fitness data streaming pipeline with the following components:
* Confluent Platform
* ELK Stack
* Fitness Data Donation Platform
* Fitness Data Kafka Producer

## Setup ELK Stack

For reference see the following tutorials [1](https://www.linode.com/docs/kubernetes/how-to-deploy-the-elastic-stack-on-kubernetes/
) & [2](https://logz.io/blog/deploying-the-elk-stack-on-kubernetes-with-helm/).


1. Deploy Kafka Elasticsearch connector

2. Deploy Elasticsearch:
```
$ helm repo add elastic https://helm.elastic.co
$ helm repo update
$ curl -O https://raw.githubusercontent.com/elastic/Helm-charts/master/elasticsearch/examples/minikube/values.yaml # Elasticsearch cluster on Minikube
$ helm install elasticsearch elastic/elasticsearch -f ./values.yaml
```

3. Deploy Kibana:
```
$ helm install --name kibana elastic/kibana
```
4. Deploy Metricbeat:
```
$ helm install --name metricbeat elastic/metricbeat
```

5. Configure Kibana

## Setup Confluent Platform, Donation Platform & Kafka Producer

Please refer to the Fitness Data Pipeline [README](../README.md) for more information about those components.