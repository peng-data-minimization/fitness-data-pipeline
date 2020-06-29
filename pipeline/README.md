# Streaming Pipeline

A Kubernetes based fitness data streaming pipeline with the following components:
* Confluent Platform
* Elasticsearch & Kibana
* Grafana & Prometheus
* Fitness Data Donation Platform
* Fitness Data Kafka Producer

## Setup Confluent Platform

Deploy the Confluent Platform with helm:
```
$ helm repo add confluentinc https://confluentinc.github.io/cp-helm-charts/
$ helm install fitness-data-pipeline confluentinc/cp-helm-charts --version 0.5.0 -f pipeline/confluent-platform/values.yml
```

## Setup Elasticsearch & Kibana

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

4. Configure Kibana
    * Enable port forwarding to access the web app
        ```
        $ kubectl port-forward deployment/kibana 5601
        ```
    * Create index pattern for index `activities`
    * Import dashboard and visualizations (see [dashboard.json](pipeline/kibana/config/dashboard.json))
        <img src="kibana/img/kibana-dashboard.png" alt="Kibana Visualization" height="300" />

5. Test Stack (see [Manual Testing](#test-pipeline-))



## Setup Monitoring (Grafana & Prometheus)

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


## Setup Donation Platform & Kafka Producer

Please refer to the Fitness Data Pipeline [README](../README.md) for more information about those components.


## Test Pipeline
**Producer -> Broker -> Connector Sink -> Elasticsearch -> Kibana**
1. Generate test activity data
    ```
    $ export NODE_IP=$(kubectl get nodes -o jsonpath='{.items[*].status.addresses[?(@.type=="InternalIP")].address}')
    $ export PRODUCER_PORT=$(kubectl get service fitness-data-donation-service -o jsonpath='{.spec.ports[?(@.name=="producer")].nodePort}')
    $ curl -X GET http://${NODE_IP}:${PRODUCER_PORT}/generate-data/start
    ```
2. Check that data can be consumed
    ```
    $ kubecexec -c cp-kafka-broker -it fitness-data-pipeline-cp-kafka-0 -- /bin/bash /usr/bin/kafka-console-consumer --bootstrap-server localhost:9092 --topic anon
    ```
3. Check that Elasticsearch connector sink works
    ```
    $ kubectl logs elasticsink-0 -f | grep "Delivered"
    [2020-06-29 09:37:03,969] INFO Delivered 90 records for anon since 2020-06-29 09:32:27 (com.datamountaineer.streamreactor.connect.utils.ProgressCounter)
    ```
4. Query Elasticsearch or look in Kibana
    ```
    $ kubectl port-forward service/elasticsearch-client 9200
    $ curl -X GET http://localhost:9200/activities/_search?size=1000\&q=id:12345678987654321 | jq .[] # 12345678987654321 is the example activity data id
    ```