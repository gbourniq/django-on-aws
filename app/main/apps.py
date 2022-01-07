"""
Application configuration objects store metadata for an application.
Some attributes can be configured in AppConfig subclasses.
Others are set by Django and read-only.
"""

from django.apps import AppConfig


class MainConfig(AppConfig):
    """
    Defines the name of the application to be installed in the
    Django settings under INSTALLED_APPS
    """

    name = "main"
    verbose_name = "Gestion des Recettes"
