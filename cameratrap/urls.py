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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#app_name = 'monkeyCT'
#urlpatterns = [
#    path('', views.IndexView.as_view(), name='index'),
#   path('<int:pk>/', views.DetailView.as_view(), name='detail'),
#   path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
#    path('<int:question_id>/vote/', views.vote, name='vote'),
#]
