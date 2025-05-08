from django.urls import path
from . import views

urlpatterns = [
    #path('<int:dan>/', views.gugu, name='gugu'),
    #path('<int:dan>/', views.gugu_template_view, name='gugu'),
    path('<int:dan>/', views.gugu, name='gugu'),
    path('', views.ajax_page, name='ajax_page'),        # ajax 페이지
    path('ajax_gugu/<int:dan>/', views.ajax_gugu, name='ajax_gugu'),  # json 응답
    path('add_ajax/', views.add_ajax_view, name='add_ajax_view'),
    path('add/', views.add_numbers, name='add_numbers'),  # POST 계산 요청용

]