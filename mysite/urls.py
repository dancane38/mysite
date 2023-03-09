from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('polls/', include('polls.urls')),
    path('cameratrap/', include('cameratrap.urls')),
    path('admin/', admin.site.urls),
]