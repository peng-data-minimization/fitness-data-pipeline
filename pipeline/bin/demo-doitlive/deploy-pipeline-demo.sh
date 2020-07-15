cd ~/workspace/helm-charts

helm install dm-pipeline-live -n live-deployment . -f values.yaml

kubectl get pods -n live-deployment -w
