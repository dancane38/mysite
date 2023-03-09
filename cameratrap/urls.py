from django.urls import path

from cameratrap import views

urlpatterns = [
    path('', views.index, name='index'),
]

#app_name = 'monkeyCT'
#urlpatterns = [
#    path('', views.IndexView.as_view(), name='index'),
#   path('<int:pk>/', views.DetailView.as_view(), name='detail'),
#   path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
#    path('<int:question_id>/vote/', views.vote, name='vote'),
#]
