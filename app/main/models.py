"""This module defines the Django models Item and Category to manage blog posts"""

from django.conf import settings
from django.db import models
from django.utils import timezone

from .mixins import BaseModelMixin


class Category(models.Model, BaseModelMixin):
    """Django model to manage blog post categories"""

    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=200, unique=True)
    summary = models.TextField()
    image = models.ImageField(upload_to=settings.UPLOADS_FOLDER_PATH)
    category_slug = models.CharField(max_length=200, unique=True)

    @classmethod
    def create(cls, dictionary):
        """
        Instantiate a Category objects using dictionaries.
        Usage: new_category = Category.create(datadict)
        """
        return cls(**dictionary)

    # pylint: disable=signature-differs
    def save(self, *args, **kwargs):
        """Resize the image on category.save()"""
        self.image = self.resize_image(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        """User-friendly string representation of the object"""
        return self.category_name

    def __repr__(self):
        """User-friendly string representation of the object"""
        return (
            f"Category=(id={self.id},category_name={self.category_name}"
            f",category_slug={self.category_slug})"
        )

    class Meta:
        verbose_name_plural = "Categories"
        app_label = "main"


class Item(models.Model, BaseModelMixin):
    """Django model to manage blog post items"""

    id = models.AutoField(primary_key=True)
    item_name = models.CharField(max_length=200, unique=True)
    summary = models.CharField(max_length=200)
    image = models.ImageField(upload_to=settings.UPLOADS_FOLDER_PATH)
    content = models.TextField()
    date_published = models.DateTimeField("date published", default=timezone.now)
    item_slug = models.CharField(max_length=200, unique=True)
    category_name = models.ForeignKey(
        Category, default=1, verbose_name="Category", on_delete=models.SET_DEFAULT,
    )
    views = models.IntegerField(default=0)

    @classmethod
    def create(cls, dictionary):
        """Instantiate Item objects using dictionaries."""
        return cls(**dictionary)

    # pylint: disable=signature-differs
    # def save(self, *args, **kwargs):
    #     """Resize the image on category.save()"""
    #     self.image = self.resize_image(self.image)
    #     super().save(*args, **kwargs)

    def increment_views(self):
        """Instance method to increment the views variable"""
        self.views += 1
        self.save()

    def __str__(self):
        """User-friendly string representation of the object"""
        return self.item_name

    def __repr__(self):
        """User-friendly string representation of the object"""
        return (
            f"Item=(id={self.id},item_name={self.item_name},item_slug={self.item_slug})"
        )

    class Meta:
        verbose_name_plural = "Items"
        app_label = "main"
