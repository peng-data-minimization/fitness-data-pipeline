#!/usr/bin/env bash

set -e

echo -e "\e[32m\nLoggin in to DockerHub...\e[0m"
docker login

echo -e "\e[32m\nBuilding and tagging docker images...\e[0m"
docker build -t kafka-fitness-data-producer -f kafka-producer/Dockerfile .
docker build -t fitness-data-donation -f donation-platform/Dockerfile .

docker tag kafka-fitness-data-producer tubpeng/kafka-fitness-data-producer
docker tag fitness-data-donation tubpeng/fitness-data-donation

echo -e "\e[32m\nPushing images at DockerHub...\e[0m"
docker push tubpeng/kafka-fitness-data-producer
docker push tubpeng/fitness-data-donation