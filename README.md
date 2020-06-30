# Fitness Data Pipeline

A Kubernetes based fitness data streaming pipeline with the following components:
* Confluent Platform
* Elasticsearch & Kibana
* Grafana & Prometheus
* Fitness Data Donation Platform
* Fitness Data Kafka Producer

## Usage

1. Donate fitness data (e.g. Strava activities)
2. Apply data minimization methods on streamed fitness data
3. Visualize anonymized or aggregated data in Kibana
<table><tr>
    <td> <img src="donation-platform/static/authorize-strava-example.png" alt="1. Strava Authorization" /> </td>
    <td> <img src="pipeline/kibana/img/kibana-dashboard.png" alt="3. Kibana Visualization" /> </td>
</tr></table>


## Dependencies

* MiniKube
* helm
* kubectl
* envsubst (gettext)


## Deployment

1. Deploy the Confluent Platform on k8s with helm:
```
$ helm repo add confluentinc https://confluentinc.github.io/cp-helm-charts/
$ helm install fitness-data-pipeline confluentinc/cp-helm-charts --version 0.5.0 -f pipeline/confluent-platform/values.yml
```

2. Create a k8s deployment for the donation-platform and the kafka-producer and expose them via a NodePort:
```
$ export STRAVA_CLIENT_ID=<client-id>
$ export STRAVA_CLIENT_SECRET=<client-secret>
$ cat deployment.yml | envsubst | kubectl apply -f -
```
3. Setup remaining pipeline components (Elasticsearch, Kibana, Grafana & Prometheus) (refer to [pipeline/README.md](pipeline/README.md))

4. Testing setup see [Manual Testing](#manual-testing)


## Development

Build images and push them to DockerHub:
```
$ ./publish-image.sh
```

Roll out the new images with k8s:
```
 $ kubectl rollout restart deployment/kafka-fitness-data-producer
```

If the deployment config files have changed, you can use rsync:
```
$ rsync -a ~workspace/fitness-data-pipeline/ root@<VM_IP>:/data/workspace/fitness-data-pipeline
$ cat deployment.yml | envsubst | kubectl apply -f -
```

### Manual Testing

**Kafka Producer**

Get IP and port of fitness-data-donation-service node:
```
$ export NODE_IP=$(kubectl get nodes -o jsonpath='{.items[*].status.addresses[?(@.type=="InternalIP")].address}')
$ export DONATION_PORT=$(kubectl get service fitness-data-donation-service -o jsonpath='{.spec.ports[?(@.name=="donation")].nodePort}')
$ export PRODUCER_PORT=$(kubectl get service fitness-data-donation-service -o jsonpath='{.spec.ports[?(@.name=="producer")].nodePort}')
```

Start continuously sending exemplary fitness data to Kafka:
```
$ curl -X GET http://${NODE_IP}:${PRODUCER_PORT}/generate-data/start
```

**Fitness Data Donation Platform**

Enable local port forwarding to access donation platform in the local browser and donate e.g. Strava activity data:
```
$ ssh -fNT -L 7777:<NODE_IP>:<DONATION_PORT> root@<VM_IP>
$ open http://localhost:7777/authorize/strava
```

**Kafka Broker**

Send data via:
* donation platform `/authorize/strava`
* fitness data kafka-producer `/generate-data/start`
* manually
 ```
 kubectl exec -c cp-kafka-broker -it fitness-data-pipeline-cp-kafka-0 -- /bin/bash /usr/bin/kafka-console-producer --broker-list localhost:9092 --topic anon
 ```

Verify that data can be consumed:
```
$ kubectl exec -c cp-kafka-broker -it fitness-data-pipeline-cp-kafka-0 -- /bin/bash /usr/bin/kafka-console-consumer --bootstrap-server localhost:9092 --topic anon --from-beginning
```

**Kafka / Zookeeper Client Deployment**

Deploy Kafka or Zookeeper client pod to play around:
```
$ cd /data/workspace/
$ git clone https://github.com/confluentinc/cp-helm-charts.git
$ kubectl apply -f cp-helm-charts/examples/kafka-client.yaml
$ kubectl exec -it kafka-client -- /bin/bash <kafka-binary>
```
For more details see [cp-helm-charts#kafka](https://github.com/confluentinc/cp-helm-charts#kafka) and [cp-helm-charts#zookeepers](https://github.com/confluentinc/cp-helm-charts#zookeepers).

### Local Setup

To build and test the application locally, use docker-compose:
```
$ docker-compose up --build
$ open http://localhost:7777 # testing fitness-data-donation-platform
$ curl -X GET http://localhost:7778/generate-data/start # testing kafka-producer
$ docker exec $(docker ps -aqf "name=fitness-data-pipeline_kafka_1") /bin/bash -c "/opt/kafka_*/bin/kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic anon --from-beginning" # verify that messages have arrived
```

See [kafka-producer/README.md](kafka-producer/README.md) and [donation-platform/README.md](donation-platform/README.md) for more details.


## Environment Setup

The pipeline is deployed on a MiniKube Kubernetes Cluster running Ubuntu 20.04 on GCP.


1. Install MiniKube & kubectl
Follow tutorial [How To Install Minikube on Ubuntu](https://computingforgeeks.com/how-to-install-minikube-on-ubuntu-debian-linux/), but don't use additonal hypervisor and instead install MiniKube with `--driver=none`

2. Install Helm
```
$ curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
$ chmod 700 get_helm.sh
$ ./get_helm.sh
```

3. Install further tooling (recommended)
```
$ apt-get update -y && apt-get install gettext-base
$ helm plugin install https://github.com/databus23/helm-diff --version master
```

4. Configure new storage location for docker

 1. Stop Docker
```
$ systemctl stop docker
```
 2. Add `--data-root` flag to `dockerd` startup in `/lib/systemd/system/docker.service`
```diff
+ExecStart=/usr/bin/dockerd  --data-root /data/lib/docker ....
```
 3. Rsync existing data
```
$ rsync -aqxP /var/lib/docker/ /data/lib/docker
```
 4. Start docker
```
$ systemctl daemon-reload
$ systemctl start docker
```
