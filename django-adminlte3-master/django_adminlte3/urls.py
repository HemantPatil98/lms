"""django_adminlte3 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
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
from django.urls import path
from django.conf.urls import url, include
from django.views.generic.base import TemplateView
from . import sheetsapi

sheetsapi.startsheet()

from . import views,sheetsapi
urlpatterns = [
    path('',include('lms.urls')),
    path('',include('exam.urls')),
    path('', include('adminlte3_theme.urls')),
    path('admin/', admin.site.urls),
    # path('admin/include/addstudent/', views.addstudent, name='addstudent'),
    # path('admin/include/view_data/<slug:table>/',views.viewstudent, name='viewstudent'),
    # path('admin/include/view_data/<int:row>/<int:col>/<slug:value>/',sheetsapi.updatesheet,name='updatesheet')
]
