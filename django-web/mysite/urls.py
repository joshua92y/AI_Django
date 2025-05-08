"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return render(request, 'mysite/mysite_index.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # ✅ 루트 요청은 home 뷰로
    # 이하 앱 URL들
    path('gugu/', include('gugu.urls')),
    path('store/', include('store.urls')),
    path('email/', include('gmail.urls')),
    path('account/', include('account.urls')),
    path('gbook/', include('gbook.urls')),
    path('books/', include('bookstore.urls')),
    path('AItest/', include('AItest.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)