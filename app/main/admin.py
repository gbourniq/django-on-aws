"""
This module defines Admin models to map our Category and Item models so that
they can be managed via the Django admin page /admin
"""
from django.contrib import admin
from django.db import models
from tinymce.widgets import TinyMCE

from .models import Category, Item


class ItemAdmin(admin.ModelAdmin):
    """
    Class to add an Item from the Django admin page with the TinyMCE
    plugin which provides text formatting options
    """

    fieldsets = [
        ("1. Entrer le nom de la recette", {"fields": ["item_name"]}),
        ("2. Selectionner une catégorie", {"fields": ["category_name"]}),
        ("3. Ajouter une photo et les instructions", {"fields": ["image", "content"]}),
    ]
    # Add TinyMCE Widget to textfield property
    formfield_overrides = {
        models.TextField: {"widget": TinyMCE()},
    }


class CategoryAdmin(admin.ModelAdmin):
    """Class to add a Category from the Django admin page."""

    fields = ("category_name", "image")


# Register models
admin.site.register(Item, ItemAdmin)
admin.site.register(Category, CategoryAdmin)
