from django.contrib import admin
from django.db import models
from tinymce.widgets import TinyMCE

from .models import Category, Item


class ItemAdmin(admin.ModelAdmin):
    """
    Class to add an Item from the Django admin page.
    Features the TinyMCE plugin to provide text formatting options
    """

    fieldsets = [
        ("Title/date", {"fields": ["item_name", "date_published"]}),
        ("URL", {"fields": ["item_slug"]}),
        ("Parent Element", {"fields": ["category_name"]}),
        ("Content (Width ~600px)", {"fields": ["summary", "content"]}),
    ]
    # Add TinyMCE Widget to textfield property
    formfield_overrides = {
        models.TextField: {"widget": TinyMCE()},
    }


class CategoryAdmin(admin.ModelAdmin):
    """
    Class to add an Item from the Django admin page.
    """

    fieldsets = [
        (
            "Category details",
            {"fields": ["category_name", "summary", "image", "category_slug"]},
        )
    ]


# Register models
admin.site.register(Item, ItemAdmin)
admin.site.register(Category, CategoryAdmin)
