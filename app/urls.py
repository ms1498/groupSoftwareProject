from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from . import queries

urlpatterns = [
    path("", views.index, name="home"),
    path("events-data", queries.serve_events, name="serve-events"),
    path("register_event/<int:event_id>/", views.register_event, name="register_event"),
    path("qrgen", queries.qrgen, name="QR code"),
    path("discover", views.discover, name="discover"),
    path("approval", views.approval_page, name="approval"),
    path("approve_event/<int:event_id>/", views.approve_event, name="approve_event"),
    path("my-events", views.my_events, name="my-events"),
    path("organise", views.organise, name="organise"),
    path("sign-in", views.sign_in, name="sign-in"),
    path("sign-up", views.sign_up, name="sign-up"),
    path("sign-out", views.sign_out, name="sign-out"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
