"""
This module defines Admin models to map our Category and Item models so that
they can be managed via the Django admin page /admin
"""
import json
import logging
from typing import NoReturn

import boto3
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm
from django.http import HttpRequest
from tinymce.widgets import TinyMCE

from app.config import AWS_REGION, AWS_S3_CUSTOM_DOMAIN, SES_IDENTITY_ARN

from .models import Category, Item

logger = logging.getLogger(__name__)


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

    # To have the number of item views from the admin panel
    readonly_fields = ("views",)

    def save_model(
        self, request: HttpRequest, item: Item, form: ModelForm, change: bool
    ):
        super().save_model(request, item, form, change)
        self.notify_registered_users(item, is_modified=change)

    @staticmethod
    def notify_registered_users(item: Item, is_modified: bool) -> NoReturn:
        """
        Notify users via AWS SES.
        Registered emails must be manually added as SES verified identifies from
        within the AWS Console, because of the limited / sandbox environment.
        For a production use case, raise a ticket with AWS.
        """
        if is_modified:
            logger.info("Item {item} was modified, not created. Skipping SES email")
            return

        ses_client = boto3.client("ses", region_name=AWS_REGION)

        destinations = [
            {
                "Destination": {"ToAddresses": [user.email],},
                "ReplacementTemplateData": json.dumps(
                    {
                        "base_url": f"https://{AWS_S3_CUSTOM_DOMAIN}",
                        "item_name": item.item_name,
                        "item_page_url": f"https://{AWS_S3_CUSTOM_DOMAIN}/items/{item.category_name.category_slug}/{item.item_slug}",
                        "item_image_url": item.image_thumbnail.url,
                        "action": "modifiée" if is_modified else "ajoutée",
                        "subject": "🍚 Tari-Recette mise à jour!"
                        if is_modified
                        else "🍚 Nouvelle Tari-Recette disponible!",
                        "username": user.username.title(),
                        "email": user.email,
                    }
                ),
            }
            for user in User.objects.all()
            if user.username and user.email
        ]

        if not SES_IDENTITY_ARN:
            logger.info("SES_IDENTITY_ARN not set. Skipping SES email.")
            return

        try:
            response = ses_client.send_bulk_templated_email(
                Source="tari-alerts@tari.kitchen",
                SourceArn=SES_IDENTITY_ARN,
                ReplyToAddresses=[],
                DefaultTags=[],
                Template="ItemCreatedOrModifiedNotification",  # TODO: remove hardcoded TemplateName. Could use TemplateArn from Cfn
                DefaultTemplateData=json.dumps(
                    {"base_url": f"https://{AWS_S3_CUSTOM_DOMAIN}"}
                ),
                Destinations=destinations,
            )
            logger.info(f"SES notification was successful. response: {response}")
        except Exception as ses_err:
            logger.error(f"Failed to send SES email notification: {repr(ses_err)}")


class CategoryAdmin(admin.ModelAdmin):
    """Class to add a Category from the Django admin page."""

    fields = ("category_name", "image")


# Register models
admin.site.register(Item, ItemAdmin)
admin.site.register(Category, CategoryAdmin)
