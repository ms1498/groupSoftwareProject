from django.urls import path
from .views import serve_events_txt

from . import views
from .views import serve_events_txt

urlpatterns = [
    path("", views.index, name="home"),
    path('events-data/', serve_events_txt, name='serve_events_txt'),
    path("discover", views.discover, name="discover"),
    path("my-events", views.myEvents, name="my-events"),
    path("organise", views.organise, name="organise"),
    path("sign-in", views.signIn, name="signIn"),
    path("sign-up", views.signUp, name="signUp"),
    path('events-data/', serve_events_txt, name='serve_events_txt'),
]