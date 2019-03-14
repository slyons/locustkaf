#!/bin/bash

# Make sure that the AZ file share is created before deploying these!

kubectl apply -f master-deploy.yaml
kubectl apply -f deployment.yaml
kubectl apply -f deployment-nymph.yaml

# Wait for the external load balancer to acquire an IP

echo "Waiting for external IP..."
kubectl get service locust-master --no-headers=true --watch-only=true -w -o custom-columns=IP:.status.loadBalancer.ingress[0].ip