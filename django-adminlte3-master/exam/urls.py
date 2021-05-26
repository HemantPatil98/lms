from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from . import views
urlpatterns = [
    # path('',include('django_adminlte3.urls')),
    path('add/questions/',views.add_questions,name='add_questions'),
    path('view/questions/<int:pageno>/',views.view_questions,name='view_questions'),
    path('mcq/exam/',views.mcq_exam,name='mcq_exam'),
    path('mcq_validate/',views.mcq_validate,name='mcq_validate'),
    path('practicle/exam/',views.practicle_exam,name='practicle_exam'),
    path('savepracticle/',views.savepracticle,name='save_practical'),
    path('saveprogram/',views.saveprogram,name='save_program'),
    path('practicle_validate/',views.practicle_validate,name='practicle_validate'),
    path('view/practicle/',views.view_practicle,name='view_practicle'),
    path('marks/practicle/',views.marks_practicle,name='marks_practicle'),
    path('setprogrammarks/',views.setprogrammarks,name='setprogrammarks'),
    # path('view/practicle//',views.view_practicle_validate,name='view_practicle'),
    path('get/answers/',views.get_answers,name='get_answers'),
    path('getdata_practicle/',views.getdata_practicle,name='getdata_practicle'),
    path('sync/questions/',views.sync_questions,name='sync_questions'),
]