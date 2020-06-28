# Streaming Pipeline

A Kubernetes based fitness data streaming pipeline with the following components:
* Confluent Platform
* ELK Stack
* Fitness Data Donation Platform
* Fitness Data Kafka Producer

## Setup ELK Stack

For reference see the following tutorials [1](https://www.linode.com/docs/kubernetes/how-to-deploy-the-elastic-stack-on-kubernetes/
) & [2](https://logz.io/blog/deploying-the-elk-stack-on-kubernetes-with-helm/).

Warning: Unfortunately, the lensesio Kafka Elasticsearch connector does not yet support Elasticsearch 7 and the elastic/elasticsearch helm repo does not support a compatible Elasticsearch 6.x version. Therefore, the deprecated stable/elasticsearch helm chart with version 1.32.2 (Elasticsearch 6.8.2) is used instead. To prevent compatibility issues with Kibana an old version is used as well.

1. Deploy Kafka Elasticsearch connector
```
$ helm repo add landoop https://lensesio.github.io/kafka-helm-charts
$ helm install elasticsink landoop/kafka-connect-elastic6-sink -f pipeline/kafka-connect-elastic-sink/values.yml
```

2. Deploy Elasticsearch:
```
$ helm repo add stable https://kubernetes-charts.storage.googleapis.com/
$ helm install elasticsearch stable/elasticsearch --version 1.32.2 -f pipeline/elastic/values.yml
```

3. Deploy Kibana:
```
$ helm upgrade kibana stable/kibana --version 3.2.6 --set env.ELASTICSEARCH_HOSTS=http://elasticsearch-client:9200
```

4. Deploy Monitoring

JMX Metrics are enabled by default for all Confluent Platform components, Prometheus JMX Exporter is installed as a sidecar container along with all Pods.

 1. Install Prometheus and Grafana in same Kubernetes cluster using helm:
 ```
 $ helm install stable/prometheus
 $ helm install stable/grafana
 # Alternatively:
 $ helm install my-prometheus-operator stable/prometheus-operator
 ```

 2. Login to Grafana (username: `admin`)
 ```
 $ kubectl port-forward svc/grafana 80
 $ kubectl get secret grafana -o jsonpath="{.data.admin-password}" | base64 --decode
 ```

 3. Add Prometheus as Data Source in Grafana (http://prometheus-server:80)

 4. Import Confluent dashboard into Grafana ([confluent-grafana-dashboard.json](monitoring/confluent-grafana-dashboard.json))

5. Configure Kibana

## Setup Confluent Platform, Donation Platform & Kafka Producer

Please refer to the Fitness Data Pipeline [README](../README.md) for more information about those components.