from django.urls import path

from . import views

from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("qrgen", views.qrgen, name="QR code"),
    #path("home", views.showStats, name="home"),
    #path("calculate", views.calculateRiskPage, name="calculateRiskPage"),
    #path("calculationExplain", views.calculationExplain, name="calculationExplain"),
]