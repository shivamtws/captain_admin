
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index,name="index"),
    path('login', views.login,name="login"),
    path('prompt', views.prompt,name="prompt"),
    path('data', views.data,name="data"),
    path('logout/', views.logout_view, name="logout"),  # Added logout URL

]
