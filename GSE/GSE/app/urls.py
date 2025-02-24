from django.urls import path
from .views import serve_events_txt
from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("events-data", serve_events_txt, name="serve_events_txt"),
    path("discover", views.discover, name="discover"),
    path("my-events", views.my_events, name="my-events"),
    path("organise", views.organise, name="organise"),
    path("sign-in", views.sign_in, name="sign-in"),
    path("sign-up", views.sign_up, name="sign-up"),
    path("sign-out", views.sign_out, name="sign-out"),
<<<<<<< Updated upstream:GSE/GSE/app/urls.py
    path("qrgen", views.qrgen, name="QR code"),
]
=======
    path('password_reset/', views.password_reset, name='password_reset'),
    path('password_reset/done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', views.password_reset_complete, name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
>>>>>>> Stashed changes:app/urls.py
