from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("events-data", views.serve_events_txt, name="serve-events-txt"),
    path("discover", views.discover, name="discover"),
    path("my-events", views.my_events, name="my-events"),
    path("organise", views.organise, name="organise"),
    path("sign-in", views.sign_in, name="sign-in"),
    path("sign-up", views.sign_up, name="sign-up"),
    path("sign-out", views.sign_out, name="sign-out"),
    path("qrgen", views.qrgen, name="QR code"),
]
