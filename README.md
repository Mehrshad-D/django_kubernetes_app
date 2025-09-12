my-django-kube-app
Getting Started
To get your Django dashboard and PostgreSQL database running on a Kubernetes cluster, follow these steps. This guide assumes you have a working Kubernetes cluster and the kubectl command-line tool configured.

Features
Kubernetes Cluster
Fully Containerized Stack: The entire application, including both the Django dashboard and the PostgreSQL database, runs as pods within the Kubernetes cluster.

Kubernetes Service Integration: The Django application connects to the PostgreSQL database using its internal Kubernetes service name, ensuring reliable and stable communication.

Django Dashboard
Cluster Visualization: View a live list of all nodes and pods in your cluster.

Real-Time Metrics: Monitor key metrics like CPU and memory usage of your pods and nodes.

Database Integration: The dashboard uses a PostgreSQL database to store and manage operational data.

Architecture
The application is built on a simple, robust architecture where the Django web application and its PostgreSQL database are both deployed as self-contained pods within the Kubernetes cluster. This design leverages the cluster's internal DNS to facilitate secure communication between the two components.

Installation and Deployment
Step 1: Deploy to Kubernetes
First, apply the provided Kubernetes manifest files to deploy the PostgreSQL database, the Django application, and their corresponding services.

kubectl apply -f k8s/

Step 2: Access the Dashboard
Once the pods are in a Running state, you can access the dashboard through the Kubernetes Ingress. Depending on your Ingress controller setup, you will need to find the external IP address or DNS name of the Ingress to navigate to the dashboard in your web browser.
