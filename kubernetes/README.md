# Kubernetes Declarative Manifests

Place the Kubernetes declarative manifests in this directory.

## namespace.yaml

> kubectl create ns sandbox --dry-run=client -o yaml > namespace.yaml

## deploy.yaml

> kubectl create deploy techtrends --image birajpoddar/techtrends:latest -n sandbox --port 3111 --dry-run=client -o yaml > deploy.yaml

Added the resources, readiness and liveliness probes later

## service.yaml

> kubectl expose --name=techtrends --port=4111 --target-port=3111 -f deploy.yaml --type=ClusterIP -n sandbox --dry-run=client -o yaml > service.yaml

## balancer.yaml

> kubectl expose --name=techtrends-balancer --port=6111 --target-port=3111 -f service.yaml --type=LoadBalancer -n sandbox --dry-run=client -o yaml > balancer.yaml
