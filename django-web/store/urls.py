# store/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.product_add, name='product_add'),
    path('', views.product_search_list, name='product_list'),
    path('detail/', views.product_detail_by_query, name='product_detail_by_query'),
    path('edit/', views.product_edit, name='product_edit'),  # 수정 폼
    path('delete/', views.product_delete, name='product_delete'),  # 삭제 API
    path('copy/', views.product_copy, name='product_copy'),
]