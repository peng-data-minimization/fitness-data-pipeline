 #!/usr/bin/env bash

set -e

kubectl exec -c cp-kafka-broker -it dm-pipeline-cp-kafka-0 -- /bin/bash /usr/bin/kafka-topics --zookeeper dm-pipeline-cp-zookeeper:2181 --alter --topic _schemas --config cleanup.policy=compact