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

3. Build the application image

```bash
docker build -t customer-event-processor:v1 .
```

Load the image into Minikube:

```bash
minikube image load customer-event-processor:v1
```

4. Deploy the application

Apply the Kubernetes manifests:

```bash
kubectl apply -f k8s/deployment.yaml

kubectl apply -f k8s/service.yaml
```

Check the Deployment and pods:

```bash
kubectl get deployments

kubectl get pods
```

The application should start with two replicas.

5. Access the application

Forward the Kubernetes Service to your local machine:

```bash
kubectl port-forward service/customer-event-processor 8000:80
```

In another terminal, test the application:

```bash
curl http://localhost:8000/
```

Check the health endpoint:

```bash
curl http://localhost:8000/health
```

Introduce some CPU-intensive work:

```bash
curl "http://localhost:8000/process?duration=2"
```

The response includes information about the application instance and the work performed.

The port-forward is useful for testing an individual access path. For load-generation experiments, use the Kubernetes Service from inside the cluster so requests can be distributed across its backing pods.

