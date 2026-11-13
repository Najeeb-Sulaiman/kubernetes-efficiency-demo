# Kubernetes Efficiency: Beyond Rightsizing

## Prerequisites

You will need:

- Docker
- Minikube
- kubectl
- Python (for the load generator, if running locally)
- Familiarity with containers and Kubernetes

This project uses Minikube so you can experiment locally without requiring a managed Kubernetes cluster or cloud account.

## Getting started

1. Clone the repository

```bash
git clone https://github.com/Najeeb-Sulaiman/kubernetes-efficiency-demo.git

cd kubernetes-efficiency-demo
```

2. Start Minikube
```bash
minikube start --driver=docker
```

Check that your Kubernetes node is ready:

```bash
kubectl get nodes
```
