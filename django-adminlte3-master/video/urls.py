from django.urls import path
from . import views

urlpatterns = [
    path('video/<slug:course>/',views.video,name='video'),
    path('videoframe/<slug:course>/<slug:video>/', views.videoframe, name='videoframe'),
    path('v/<slug:course>/<slug:video>/', views.v, name='v'),
    path('thumb/', views.thumb, name='thumb'),
    path('videopermissons/', views.videopermissions, name='videopermissions'),
    path('watched_video/',views.watched_video, name='watched_video')
    ]