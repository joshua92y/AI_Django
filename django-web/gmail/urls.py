import os
from django.urls import path
from . import views

app_name='gmail'

urlpatterns = [
    path('', views.index, name='index'), 
    path('send/', views.send_email, name='send_email')
]