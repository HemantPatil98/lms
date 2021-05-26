
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('',include('django_adminlte3.urls')),
    path('video/<slug:course>/',views.video,name='video'),
    path('videoframe/<slug:course>/<slug:video>/', views.videoframe, name='videoframe'),
    path('v/<slug:course>/<slug:video>/', views.v, name='v'),
    path('thumb/', views.thumb, name='thumb'),
    path('videopermissons/', views.videopermissions, name='videopermissions'),
    # path('media/', views.blank, name='blank'),
    path('watched_video/',views.watched_video, name='watched_video')
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)