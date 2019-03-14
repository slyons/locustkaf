#!/bin/bash

kubectl scale deployments/locust-nymph --replicas=0
kubectl scale deployments/locust-master --replicas=0

kubectl scale deployments/locust-master --replicas=1
sleep 5
kubectl scale deployments/locust-nymph --replicas=1