########### DM TOOL PRESENTATION ###########

# open https://github.com/peng-data-minimization
# open https://data-minimization-tools.readthedocs.io/en/latest/
# open https://github.com/peng-data-minimization/minimizer-poc/blob/master/presentation/example_config.yml


########### USE CASE PRESENTATION ###########

# show donation platform website
open http:/show-me-your-bicep.ml/

# show pipeline deployment
helm list
kubectl get pods
kubectl get pods | grep dm-pipeline-spi

# deploy spi worker with helm
# note that when the spi is installed by itself not as part of dm-helm-charts/data-minimization-pipeline,
# the helm values file fitness-data-minimization-tasks.yml does not need the top-level yaml key `spi:`
cd ~/workspace/helm-charts/subcharts/spi
helm install dm-pipeline-spi -n demo . -f ./values.yaml -f ~/workspace/fitness-data-pipeline/pipeline/spi/fitness-data-minimization-tasks.yml
kubectl get pods -w

# illustrate spi worker task config update with helm
# fitness-data-minimization-tasks-empty.yml has to be created first
# helm diff upgrade dm-pipeline-spi -n demo . --reuse-values -f ~/workspace/fitness-data-pipeline/pipeline/spi/fitness-data-minimization-tasks-empty.yml

# -> Upload .FIT file (API /file/upload)

# Or altertatively, generate test activity data via API...
# kubectl port-forward deployment/kafka-fitness-data-producer 7778 > /dev/null &
# for i in {1..10}; do curl -X GET http://localhost:7778/generate-data/start; done

# Checking that Elasticsearch connector sink works...
kubectl logs dm-pipeline-0 | grep "Delivered" | tail -n 10

# Checking that Elasticsearch connector sink works...
kubectl port-forward service/dm-pipeline-elasticsearch-client 9200 > /dev/null &
curl -s -X GET http://localhost:9200/processed*/_search?size=10\&q=*:* | jq .[] | head -n 25

# Checking Kibana...
kubectl port-forward deployment/dm-pipeline-kibana 5601 > /dev/null &
open 'http://localhost:5601/app/kibana'

# -> Visualize anonymized route (.FIT file)
