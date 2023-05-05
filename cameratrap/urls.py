from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from cameratrap import views

app_name = 'cameratrap'
urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('uploads/', views.UploadFileView, name='upload'),
    path("<int:video_pkid>/process", views.SyncProcessVideoView, name='process'),
    path("<int:video_pkid>/asyncprocess", views.ASyncProcessVideoView, name='asyncprocess'),
    path("<int:video_pkid>/<int:video_frame_pkid>/coco", views.CocoVideoFrameView, name='coco'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

