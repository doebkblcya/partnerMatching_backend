from django.urls import path
from . import views

urlpatterns = [
    path('add', views.TeamAddView.as_view()),
    path('list', views.TeamListView.as_view()),
    path('join', views.TeamJoinView.as_view()),
    path('list/my/join', views.TeamListMyJoinView.as_view()),
    path('list/my/create', views.TeamListMyCreateView.as_view()), 
    path('quit', views.TeamQuitView.as_view()), 
    path('delete', views.TeamDeleteView.as_view()), 
    path('get', views.TeamGetView.as_view()),
    path('update', views.TeamUpdateView.as_view()),
]