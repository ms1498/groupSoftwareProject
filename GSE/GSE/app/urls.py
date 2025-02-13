from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("discover", views.discover, name="discover"),
    path("myEvents", views.myEvents, name="myEvents"),
    path("organise", views.organise, name="organise"),
    path("signIn", views.signIn, name="signIn"),
    path("signUp", views.signUp, name="signUp"),
]