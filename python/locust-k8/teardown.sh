#!/bin/bash

kubectl delete --ignore-not-found=true --filename=master-deploy.yaml,deployment.yaml,deployment-nymph.yaml