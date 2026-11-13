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

Pay attention to the difference between resource capacity, allocatable resources, requested resources and actual consumption.

### Experiment 2: Observe Horizontal Pod Autoscaling

Enable Metrics Server:

```bash
minikube addons enable metrics-server
```

Deploy the HPA configuration:

```bash
kubectl apply -f k8s/hpa.yaml
```

Inspect the autoscaler:

```bash
kubectl get hpa

kubectl describe hpa customer-event-processor
```

The example HPA configuration uses:

- Minimum replicas: 2
- Maximum replicas: 6
- Target CPU utilisation: 50%

Remember that HPA's CPU utilisation target is calculated relative to the CPU requests.

For example, with a CPU request of `250m` and a target utilisation of `50%`, the target average CPU consumption is approximately `125m` per pod.

Now, introduce concurrent requests using the load generator:

```bash
python load.py
```

The load generator should send concurrent requests to the Kubernetes Service and maintain sufficient workload pressure to trigger scaling.

Observe the autoscaler:

```bash
kubectl get hpa -w
```

In another terminal:

```bash
kubectl get pods -w
```

**You should observe:**

- How does CPU utilisation change when load is introduced?
- When does HPA increase the desired replica count?
- How long does it take for new pods to become Ready?
- What happens when the load is removed?
- Does the replica count immediately return to its minimum?

Don't just watch the replica count. Try to understand why it changes and what influences the timing.

### Experiment 3: Why is my pod Pending when the node has unused CPU?

This experiment demonstrates one of the most important concepts in Kubernetes resource management.

A node can have relatively low actual CPU consumption while having very little unallocated CPU capacity from the scheduler's perspective.

Consider this simplified example:

| Metric | CPU |
| ---- | ----|
| Node allocatable CPU | 2000m |
| Existing pod requests | 1800m
| Actual CPU consumption | 700m
| New pod request | 500m

Although actual CPU consumption is only 700m, the scheduler accounts for 1800m of existing requests.

Adding another pod requesting 500m would require:

```bash
1800m + 500m = 2300m
```

The node only has 2000m of allocatable CPU.

Consequently, the scheduler cannot place the new pod on that node based on CPU capacity.

**Experiment:** Introduce a resource-reservation pod to consume most of the node's remaining schedulable CPU capacity.

Inspect the node's resource accounting:

```bash
kubectl describe node minikube
```

Use the Allocated resources section to understand the existing requests.

Then apply the capacity-reservation manifest:

```bash
kubectl apply -f k8s/capacity-reservation.yaml
```

Adjust its CPU request based on the actual available scheduling capacity of your node. Don't assume a fixed value will work across different Minikube configurations.

Reintroduce workload pressure and observe the pods:

```bash
kubectl get pods -w
```

Inspect any Pending pod:

```bash
kubectl describe pod <pending-pod-name>
```

Look for scheduling events such as:

```bash
FailedScheduling
Insufficient cpu
```

The key takeaway here is that Actual CPU consumption and schedulable CPU capacity are not the same thing.
