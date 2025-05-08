# gbook/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.gbook_list, name='gbook_list'),
    path('new/', views.gbook_create, name='gbook_create'),
    path('<int:pk>/', views.gbook_detail, name='gbook_detail'),  # ✅ 추가
    path('<int:pk>/edit/', views.gbook_edit, name='gbook_edit'),      # ✅ 수정
    path('<int:pk>/delete/', views.gbook_delete, name='gbook_delete'),# ✅ 삭제
    path('file/<int:pk>/delete/', views.gbook_file_delete, name='gbook_file_delete')

]