from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pods/', views.list_pods, name='list_pods'),
    path('nodes/', views.list_nodes, name='list_nodes'),
    path('create-dummy-resource/', views.create_dummy_resource, name='create_dummy_resource'),
    path('metrics/', views.get_simulated_metrics, name='get_simulated_metrics'),
    path('messages/save/', views.save_message, name='save_message'),
    path('messages/list/', views.list_messages, name='list_messages'),
    path('healthz/', views.health_check, name='health_check'),
]
