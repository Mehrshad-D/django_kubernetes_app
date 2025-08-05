# kube/views.py

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from kubernetes import client, config
from django.conf import settings
from django.db import IntegrityError, OperationalError
import random
from .models import Message 
from kubernetes.client.rest import ApiException 
# from django.views.decorators.csrf import csrf_exempt


_KUBE_API_CLIENT = None
_KUBE_CONFIG_LOAD_STATUS = 'Not Attempted'
_KUBE_CLIENT_CONFIG = None

# Function to load Kubernetes configuration
def _load_kube_config_once():
    global _KUBE_API_CLIENT, _KUBE_CONFIG_LOAD_STATUS, _KUBE_CLIENT_CONFIG
    if _KUBE_API_CLIENT: 
        return True

    try:
        # Try to load in-cluster config first (for running inside Kubernetes)
        # Load config into a Configuration object
        _KUBE_CLIENT_CONFIG = client.Configuration()
        config.load_incluster_config(client_configuration=_KUBE_CLIENT_CONFIG)
        
        # Set this configuration as the default for all subsequent client calls
        # This is important for other API clients that might not take a config object directly
        client.Configuration.set_default(_KUBE_CLIENT_CONFIG) 
        
        _KUBE_API_CLIENT = client.CoreV1Api()
        _KUBE_CONFIG_LOAD_STATUS = 'Loaded (In-Cluster)'
        return True
    except config.ConfigException:
        try:
            # If not in-cluster, try to load from default kubeconfig or specified path
            _KUBE_CLIENT_CONFIG = client.Configuration()
            if hasattr(settings, 'KUBERNETES_CONFIG_PATH') and settings.KUBERNETES_CONFIG_PATH:
                config.load_kube_config(config_file=settings.KUBERNETES_CONFIG_PATH, client_configuration=_KUBE_CLIENT_CONFIG)
            else:
                config.load_kube_config(client_configuration=_KUBE_CLIENT_CONFIG)
            
            client.Configuration.set_default(_KUBE_CLIENT_CONFIG)
            _KUBE_API_CLIENT = client.CoreV1Api() 
            _KUBE_CONFIG_LOAD_STATUS = 'Loaded (From Kubeconfig)'
            return True
        except Exception as e:
            _KUBE_CONFIG_LOAD_STATUS = f"Failed to load: {e}"
            print(f"Error loading kubeconfig: {e}")
            _KUBE_API_CLIENT = None
            _KUBE_CLIENT_CONFIG = None
            return False
    except Exception as e:
        _KUBE_CONFIG_LOAD_STATUS = f"Unexpected error during Kubeconfig load: {e}"
        print(f"Unexpected error loading kubeconfig: {e}")
        _KUBE_API_CLIENT = None
        _KUBE_CLIENT_CONFIG = None
        return False

# Health check endpoint
def health_check(request):
    return HttpResponse("OK", status=200)

# Main page view
def index(request):
    context = {
        'kube_config_status': _KUBE_CONFIG_LOAD_STATUS,
    }
    # Attempt to load kubeconfig if not already loaded (for displaying status on main page)
    if not _KUBE_API_CLIENT:
        _load_kube_config_once()
    return render(request, 'index.html', context) 

# View to list pods
def list_pods(request):
    if not _load_kube_config_once():
        return render(request, 'error.html', {"error_message": _KUBE_CONFIG_LOAD_STATUS}, status=500) 
    
    try:
        # Use the globally stored API client
        pods = _KUBE_API_CLIENT.list_pod_for_all_namespaces(watch=False)
        pod_list = []
        for i in pods.items:
            pod_list.append({
                "name": i.metadata.name,
                "namespace": i.metadata.namespace,
                "status": i.status.phase,
                "node_name": i.spec.node_name
            })
        return render(request, 'pods.html', {"pods": pod_list}) 
    except client.ApiException as e:
        return render(request, 'error.html', {"error_message": f"Kubernetes API error: {e.reason} (Status: {e.status})"}, status=e.status) 
    except Exception as e:
        return render(request, 'error.html', {"error_message": f"An unexpected error occurred: {e}"}, status=500) 

# View to list nodes and their status 
def list_nodes(request):
    if not _load_kube_config_once():
        return render(request, 'error.html', {"error_message": _KUBE_CONFIG_LOAD_STATUS}, status=500) 
    
    try:
        nodes = _KUBE_API_CLIENT.list_node(watch=False)
        node_list = []
        for node in nodes.items:
            status = {}
            for condition in node.status.conditions:
                status[condition.type] = condition.status
            
            addresses = [{"type": addr.type, "address": addr.address} for addr in node.status.addresses]

            node_list.append({
                "name": node.metadata.name,
                "status": status.get('Ready', 'Unknown'),
                "addresses": addresses,
                "capacity": node.status.capacity,
                "allocatable": node.status.allocatable
            })
        return render(request, 'nodes.html', {"nodes": node_list}) 
    except client.ApiException as e:
        return render(request, 'error.html', {"error_message": f"Kubernetes API error: {e.reason} (Status: {e.status})"}, status=e.status) 
    except Exception as e:
        return render(request, 'error.html', {"error_message": f"An unexpected error occurred: {e}"}, status=500) 

# View to create a dummy resource (ConfigMap)
def create_dummy_resource(request):
    if not _load_kube_config_once():
        return render(request, 'error.html', {"error_message": _KUBE_CONFIG_LOAD_STATUS}, status=500) 
    
    if request.method == 'POST':
        try:
            namespace = "default"
            configmap_name = f"dummy-configmap-{random.randint(1000, 9999)}"

            body = client.V1ConfigMap(
                api_version="v1",
                kind="ConfigMap",
                metadata=client.V1ObjectMeta(name=configmap_name),
                data={"message": "This is a dummy configmap created by Django app", "timestamp": str(random.random())}
            )
            api_response = _KUBE_API_CLIENT.create_namespaced_config_map(namespace=namespace, body=body)
            
            context = {
                "success": True,
                "message": f"ConfigMap '{api_response.metadata.name}' created successfully in namespace '{namespace}'.",
                "resource_name": api_response.metadata.name,
                "resource_kind": "ConfigMap"
            }
            return render(request, 'dummy_resource_status.html', context, status=201) 
        except client.ApiException as e:
            context = {
                "success": False,
                "message": f"Failed to create ConfigMap: Kubernetes API error: {e.reason} (Status: {e.status})",
                "error_details": e.body
            }
            return render(request, 'dummy_resource_status.html', context, status=e.status) 
        except Exception as e:
            context = {
                "success": False,
                "message": f"An unexpected error occurred while creating ConfigMap: {e}",
            }
            return render(request, 'dummy_resource_status.html', context, status=500)
    else:
        return redirect('index') 

def get_simulated_metrics(request):
    context = {
        'pod_cpu_metrics': [], # Initialize empty list for metrics
        'metrics_error': None, # Initialize for potential errors
    }

    if not _load_kube_config_once():
        context['metrics_error'] = _KUBE_CONFIG_LOAD_STATUS
        return render(request, 'metrics_display.html', context)

    try:
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()

        # Use CustomObjectsApi for metrics
        api = client.CustomObjectsApi()
        
        # Get pod metrics
        metrics = api.list_namespaced_custom_object(
            group="metrics.k8s.io",
            version="v1beta1",
            namespace="hamravesh-project",
            plural="pods"
        )

        # Process metrics - ensure this matches your template structure
        # for item in metrics.get('items', []):
        #     # Check if this is a django-app pod
        #     labels = item.get('metadata', {}).get('labels', {})
        #     if labels.get('app') == 'django-app':
        #         for container in item.get('containers', []):
        #             if container.get('name') == 'django-app':
        #                 context['pod_cpu_metrics'].append({
        #                     'name': item['metadata']['name'],  # Must match template
        #                     'cpu_usage': container['usage'].get('cpu', 'N/A'),  # Must match template
        #                     'memory_usage': container['usage'].get('memory', 'N/A')  # Must match template
        #                 })

        # In your get_pod_metrics function
        for item in metrics.get('items', []):
            metadata = item.get('metadata', {})
            pod_name = metadata.get('name', '')
            
            # Show all pods in namespace
            for container in item.get('containers', []):
                context['pod_cpu_metrics'].append({
                    'name': pod_name,
                    'cpu_usage': container['usage'].get('cpu', 'N/A'),
                    'memory_usage': container['usage'].get('memory', 'N/A')
                })  
                
        total_cpu_millicores = 0
        for pod in context['pod_cpu_metrics']:
            cpu_usage = pod['cpu_usage']
            if cpu_usage.endswith('n'):
                cpu_millicores = int(cpu_usage[:-1]) / 1e6  # Convert nanocores to millicores
            elif cpu_usage.endswith('u'):
                cpu_millicores = int(cpu_usage[:-1]) / 1000  # Convert microcores to millicores
            elif cpu_usage.endswith('m'):
                cpu_millicores = int(cpu_usage[:-1])  # Already in millicores
            else:
                cpu_millicores = int(cpu_usage) * 1000  # Assume CPU cores to millicores
            total_cpu_millicores += cpu_millicores

        average_cpu = total_cpu_millicores / len(context['pod_cpu_metrics'])

        # Threshold: if average CPU > 400m, increase replicas
        if average_cpu > 10:
            scale_deployment("django-app-deployment", "hamravesh-project", 3)  # Increase to 5
        elif average_cpu < 5 and len(context['pod_cpu_metrics']) > 1:
            scale_deployment("django-app-deployment", "hamravesh-project", 1)  # Decrease to 1
                            

    except ApiException as e:
        error_body = e.body.decode('utf-8') if e.body else 'N/A'
        context['metrics_error'] = f"Kubernetes Metrics API Error: {e.status} - {e.reason}. Details: {error_body}. Check RBAC permissions for 'metrics.k8s.io'."
        print(f"Kubernetes Metrics API Error: {e.status} - {e.reason} - {error_body}")
    except Exception as e:
        context['metrics_error'] = f"An error occurred while fetching metrics: {e}"
        print(f"Error fetching metrics: {e}")

    return render(request, 'metrics_display.html', context) 

from kubernetes import client, config
from kubernetes.client.rest import ApiException

def scale_deployment(deployment_name, namespace, replicas):
    try:
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()

        apps_v1 = client.AppsV1Api()
        scale = {
            'spec': {
                'replicas': replicas
            }
        }
        response = apps_v1.patch_namespaced_deployment_scale(
            name=deployment_name,
            namespace=namespace,
            body=scale
        )
        print(f"Scaled {deployment_name} to {replicas} replicas.")
        return True
    except ApiException as e:
        print(f"API Exception when scaling deployment: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


# --- Database Interaction Views ---
# @csrf_exempt
def save_message(request):
    if request.method == 'POST':
        message_text = request.POST.get('message_text', '').strip()
        if message_text:
            try:
                Message.objects.create(text=message_text)
                return JsonResponse({"status": "success", "message": "پیام با موفقیت ذخیره شد."}, status=201)
            except IntegrityError:
                return JsonResponse({"status": "error", "message": "خطا در ذخیره پیام: مشکل یکتایی."}, status=400)
            except OperationalError as e:
                return JsonResponse({"status": "error", "message": f"خطا در اتصال به دیتابیس: {e}. مطمئن شوید دیتابیس آماده است."}, status=500)
            except Exception as e:
                return JsonResponse({"status": "error", "message": f"خطای ناشناخته در ذخیره پیام: {e}"}, status=500)
        else:
            return JsonResponse({"status": "error", "message": "متن پیام نمی‌تواند خالی باشد."}, status=400)
    return JsonResponse({"status": "info", "message": "این نقطه پایانی برای ذخیره پیام (POST) است."}, status=200)

def list_messages(request):
    try:
        messages = Message.objects.all().order_by('-created_at')[:20]
        messages_data = [{"text": msg.text, "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M:%S")} for msg in messages]
        return JsonResponse({"messages": messages_data}, status=200)
    except OperationalError as e:
        return JsonResponse({"status": "error", "message": f"خطا در اتصال به دیتابیس: {e}. مطمئن شوید دیتابیس آماده است."}, status=500)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"خطای ناشناخته در دریافت پیام‌ها: {e}"}, status=500)
