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
    path('practicle/exam/',views.practicle_exam,name='practicle_exam'),
    path('mcq_validate/',views.mcq_validate,name='mcq_validate'),
    path('get/answers/',views.get_answers,name='get_answers'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)