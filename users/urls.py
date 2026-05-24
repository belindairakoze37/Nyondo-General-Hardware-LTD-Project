from django.urls import path
from . import views 


urlpatterns = [
    path('register/', views.register_user, name="register_user"),
    path("login/", views.login_user, name="login"),
    path("user_logout/", views.user_logout, name="user_logout"),
]