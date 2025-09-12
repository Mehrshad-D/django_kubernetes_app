# Kubernetes Django Project with Custom Dashboard

## 📌 Overview
This project demonstrates a **Kubernetes cluster** setup with one master node and two worker nodes, running a **Django-based web application** backed by a **PostgreSQL database**.  

In addition to deploying the application, I developed a **custom Kubernetes dashboard** that allows:
- Listing pods and nodes in the cluster
- Viewing CPU and memory metrics
- Interacting with a PostgreSQL database

This project showcases both **DevOps skills** (cluster setup, networking, scaling, RBAC, monitoring) and **application development** (Django, database integration, dashboard).

---

## ⚙️ Cluster Setup

- **Master node:** 1  
- **Worker nodes:** 2  
- **Container runtime:** containerd  
- **CNI plugin:** Calico (for pod networking)  
- **Pod CIDR:** `192.168.0.0/16`  

### Steps:
1. Initialize the cluster on the master:
   ```bash
   kubeadm init --pod-network-cidr=192.168.0.0/16
