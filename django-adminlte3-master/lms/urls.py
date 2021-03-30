from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.views.generic.base import TemplateView
from . import views,sheetsapi

urlpatterns = [
    # path('',include('django_adminlte3.urls')),
    path('',views.login_form,name='login_form'),
    path('login/',views.log_in,name='login'),
    path('logout/', views.log_out, name='logout'),
    path('index/',views.index,name='index'),
    # path('adminpannel/',views.admin,name='adminpannel'),
    path('add/student/',views.addstudent,name='addstudents'),
    path('view_data/student/',views.viewstudent,name='viewstudents'),
    path('view_data/performance/', views.viewperformance, name='viewperformance'),
    path('add/groups/',views.addgroups,name='addgroups'),
    path('view_data/groups/', views.viewgroups, name='viewgroups'),
    path('add/users/',views.addusers,name='addusers'),
    path('view_data/members/', views.viewmembers, name='viewmembers'),
    path('profile/', views.viewprofile, name='viewprofile'),
    path('attendance/', views.attendance, name='attendance'),
    path('add/notice/',views.addnotice,name='addnotice'),

    path('test/',views.test,name='test'),

    path('admin/include/view_data/<int:idvalue>/<int:row>/<int:col>/<slug:value>/<slug:cell>/', views.studentupdate, name='updatesheet'),
    path('admin/include/view_data/performance/<int:row>/<int:col>/<slug:value>/<slug:cell>/', views.studentpupdate,
         name='updatesheet')

    # path('admin/', admin.site.urls),
]
