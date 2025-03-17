"""Stores urls that link to views."""
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("?popup=thank-you", views.index, name = "home"),
    path("home", views.index, name = "home"),
    path("register_event/<int:event_id>/", views.register_event, name="register_event"),
    path("unregister_event/<int:event_id>/", views.unregister_event, name="unregister_event"),
    path("discover", views.discover, name="discover"),
    path("discover/<int:event_id>/", views.discover_shortcut, name="discover_shortcut"),
    path("discover/<str:category>/", views.category_shortcut, name="category_shortcut"),
    path("approval", views.approval_page, name="approval"),
    path("approve_event/<int:event_id>/", views.approve_event, name="approve_event"),
    path("my-events", views.my_events, name="my-events"),
    path("organise", views.organise, name="organise"),
    path("edit_event/<int:event_id>/", views.edit_event, name="edit_event"),
    path("event_analytics/<int:event_id>/", views.event_analytics , name="event_analytics"),
    path("qrgen/", views.generate_qr, name="generate_qr"),
    path("sign-in", views.sign_in, name="sign-in"),
    path("sign-up", views.sign_up, name="sign-up"),
    path("sign-in-another", views.sign_in_as_another, name="sign-in-another"),
    path("terms", views.terms_and_conditions, name="terms_and_conditions"),
    path("sign-out", views.sign_out, name="sign-out"),
    path("password_reset/", views.password_reset, name="password_reset"),
    path("password_reset/done/", views.password_reset_done, name="password_reset_done"),
    path("reset/<uidb64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),
    path("reset/done/", views.password_reset_complete, name="password_reset_complete"),
    path("badge", views.badge_list, name="badge"),
    path("leaderboard", views.leaderboard, name="leaderboard"),
    path("user-data", views.user_data, name="user_data"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
