from django.apps import AppConfig

class AdminConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "web-admin"

class UWeaveConfig(AppConfig):
    name = "app"