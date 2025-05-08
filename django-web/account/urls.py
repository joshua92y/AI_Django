# account/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import CustomLoginView
from django.urls import reverse_lazy

app_name = 'account'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', CustomLoginView.as_view(template_name='account/account_index.html'), name='login'),
    path('logout/',auth_views.LogoutView.as_view(next_page=reverse_lazy('account:login')),name='logout'),  # ✅ 로그인 페이지로 리디렉션
    #path('logout/', views.logout, name='logout'),
    path('signup/', views.signup,name='signup'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]