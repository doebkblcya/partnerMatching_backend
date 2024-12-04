from django.urls import path
from . import views

urlpatterns = [
    path('login', views.UserLoginView.as_view()),
    path('logout', views.UserLogoutView.as_view()),
    path('register', views.UserRegisterView.as_view()),
    path('account/exist', views.UserAccountExistView.as_view()),
    path('current', views.CurrentUserView.as_view()),
    path('recommend', views.UserRecommendView.as_view()),
    path('match', views.UserMatchView.as_view()),
    path('update', views.UserUpdateView.as_view()),
    path('search/tags', views.UserTagSearchView.as_view()),
]