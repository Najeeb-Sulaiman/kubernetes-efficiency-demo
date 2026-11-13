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

## Experiments

The repository is organised around a series of experiments. The aim of this experiments is to understand how the different Kubernetes mechanisms interact.

### Experiment 1: Understand resource requests and limits

Let's start by inspecting the Deployment manifest:

`k8s/deployment.yaml`

The application containers have the following initial resource configuration:

```yaml
resources:
  requests:
    cpu: "250m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"
```

Before changing anything, consider asking these questions:

1. What does a CPU request of 250m actually mean?
2. Does it guarantee that the container always receives 250m of CPU?
3. What happens if the application tries to consume more CPU than its limit?
4. What happens if the container exceeds its memory limit?
5. How might reducing the CPU request affect the number of pods that can be scheduled?

**Experiment:** Change the CPU request and observe how the scheduler's resource accounting changes.

Useful commands:

```bash
kubectl describe node

kubectl top nodes

kubectl top pods
```

