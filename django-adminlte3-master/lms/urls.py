from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
    path('log_in/',views.log_in,name='login'),
    # path('admin/', admin.site.urls),
]
