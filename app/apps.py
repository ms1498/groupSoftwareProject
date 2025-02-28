"""Stores Django route to provided apps."""
from django.apps import AppConfig

class AdminConfig(AppConfig):
    """Config for the web admin interface."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "web-admin"

class UWeaveConfig(AppConfig):
    """Config for the main app."""

    name = "app"
