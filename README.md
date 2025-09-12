# Kubernetes Django Project with Custom Dashboard

## 📌 Overview
This project demonstrates a **Kubernetes cluster** setup with one master node and two worker nodes, running a **Django-based web application** backed by a **PostgreSQL database**.  

In addition to deploying the application, I developed a **custom Kubernetes dashboard** that allows:
- Listing pods and nodes in the cluster
- Viewing CPU and memory metrics
- Interacting with a PostgreSQL database

This project showcases both **DevOps skills** (cluster setup, networking, scaling, RBAC, monitoring) and **application development** (Django, database integration, dashboard).

---

## Cluster Setup

- **Master node:** 1  
- **Worker nodes:** 2  
- **Container runtime:** CRI-O  
- **CNI plugin:** Calico (for pod networking)  
- **Pod CIDR:** `192.168.0.0/16`  

### Steps:
1. Initialize the cluster on the master:
   ```bash
   kubeadm init --pod-network-cidr=192.168.0.0/16
2. Configure kubeconfig for the master node:
   ```bash
   mkdir -p $HOME/.kube
   cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
   chown $(id -u):$(id -g) $HOME/.kube/config
3. Install Calico networking:   
   ```bash
   kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
4. Join worker nodes using the kubeadm join command from the master.

   
## Application Deployment
   - **The Django application was containerized and deployed using a Deployment.
     
   - **A PostgreSQL database was deployed inside the cluster for persistent data storage.

   - **Kubernetes Services (ClusterIP and NodePort) were used for internal and external access.

## Custom Dashboard

I developed a custom web-based dashboard that integrates with the Kubernetes API and PostgreSQL database:

   - **Pod and Node Management: List all pods and nodes, with their status and metadata.

   - **Metrics Visualization: Display CPU and memory usage for workloads.

   - **Database Interaction: Connect to PostgreSQL, run queries, and visualize results.
