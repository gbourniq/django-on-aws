from django.conf import settings
from django.db import models
from django.utils import timezone

from .mixins import BaseModelMixin, JSONifyMixin


class Category(models.Model, BaseModelMixin, JSONifyMixin):
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=200, unique=True)
    summary = models.TextField()
    image = models.ImageField(upload_to=settings.UPLOADS_FOLDER_PATH)
    category_slug = models.CharField(max_length=200, unique=True)

    # List of all saved categories (property hidden from other classes)
    __category_list = None

    @classmethod
    def get_category_list(cls):
        """
        Class method to return the list of
        categories that were saved via the .save() method.
        Usage:
        > categories = Category.get_category_list()
        """
        if Category.__category_list is None:
            Category.__category_list = []
        return Category.__category_list

    def __append_to_category_list(self):
        """
        Hidden instance method to append the object
        to the class attribute __category_list
        """
        Category.get_category_list().append(self)

    @classmethod
    def create(cls, dictionary):
        """
        Class method to instantiate a Category objects using dictionaries.
        Usage:
        > new_category = Cateogory.create(datadict)
        """
        return cls(**dictionary)

    def to_json(self):
        """
        Overrides JSONify instance method 
        to return class attributes as a dictionary.
        """
        return {
            "category_name": self.category_name,
            "summary": self.summary,
            "image": self.image,
            "category_slug": self.category_slug,
        }

    def save(self, *args, **kwargs):
        """
        Override the save method to resize the image on category.save()
        and notify all registered users that a new category has been added
        """
        self.image = self.resizeImage(self.image)
        self.__append_to_category_list()
        super(Category, self).save(*args, **kwargs)
        if settings.EMAIL_HOST_USER:
            self.send_email_notification_to_users(
                subject=f"[Portfolio App Demo] New Category added!",
                message=f"A new category '{self.category_name}' has been added! Check it out here... https://www.gbournique.com/items/{self.category_slug}",
            )

    def __str__(self):
        """
        Override magic method to return a user-friendly string
        representation of the object on str(category_object)
        """
        return self.category_name

    def __repr__(self):
        """
        Override magic method to return a developer-friendly string
        representation of the object on repr(category_object)
        """
        return f"Category=(id={self.id},category_name={self.category_name},category_slug={self.category_slug})"

    class Meta:
        verbose_name_plural = "Categories"
        app_label = "main"


class Item(models.Model, BaseModelMixin, JSONifyMixin):
    id = models.AutoField(primary_key=True)
    item_name = models.CharField(max_length=200, unique=True)
    summary = models.CharField(max_length=200)
    content = models.TextField()
    date_published = models.DateTimeField(
        "date published", default=timezone.now
    )
    item_slug = models.CharField(max_length=200, unique=True)
    category_name = models.ForeignKey(
        Category,
        default=1,
        verbose_name="Category",
        on_delete=models.SET_DEFAULT,
    )
    views = models.IntegerField(default=0)

    # List of all saved categories (property hidden from other classes)
    __item_list = None

    @classmethod
    def get_item_list(cls):
        """
        Class method to return the list of
        items that were saved via the .save() method.
        Usage:
        > items = Item.get_item_list()
        """
        if Item.__item_list is None:
            Item.__item_list = []
        return Item.__item_list

    def __append_to_item_list(self):
        """
        Hidden instance method to append the object
        to the class attribute __item_list
        """
        Item.get_item_list().append(self)

    @classmethod
    def create(cls, dictionary):
        """
        Class method to instantiate Item objects using dictionaries.
        """
        return cls(**dictionary)

    def to_json(self):
        """
        Returns class attributes as a dictionary.
        """
        return {
            "item_name": self.item_name,
            "summary": self.summary,
            "content": self.content,
            "date_published": self.date_published,
            "item_slug": self.item_slug,
            "category_name": self.category_name,
        }

    def increment_views(self):
        """
        Instance method to increment the views variable
        """
        self.views += 1
        self.save()

    def save(self, *args, **kwargs):
        """
        Overrides the save method to notify all registered users
        that a new item has been added
        """
        if self not in Item.objects.all() and settings.EMAIL_HOST_USER:
            # Send notification for newly created item
            self.send_email_notification_to_users(
                subject="[Portfolio App Demo] New Item added!",
                message=f"A new item '{self.item_name}' has been added! Check it out here... https://www.gbournique.com/items/{self.category_name.category_slug}/{self.item_slug}",
            )
        super(Item, self).save(*args, **kwargs)
        if self not in Item.get_item_list():
            self.__append_to_item_list()

    def __str__(self):
        """
        Override magic method to return a user-friendly string
        representation of the object on str(item_object)
        """
        return self.item_name

    def __repr__(self):
        """
        Override magic method to return a developer-friendly string
        representation of the object on repr(item_object)
        """
        return f"Item=(id={self.id},item_name={self.item_name},item_slug={self.item_slug})"

    def __ge__(self, value):
        """
        Adds the greater or eq than behavior to compare two Item objects
        based on the number of views. This allows to sort items 
        by their number of views with items.sort().
        """
        if not isinstance(value, Item):
            raise ValueError("Can't compare Item to non-Item type")
        return self.views >= value.views

    def __lt__(self, value):
        """
        Adds the less than behavior to compare two Item objects
        based on the number of views. This allows to sort items 
        by their number of views with items.sort().
        """
        if not isinstance(value, Item):
            raise ValueError("Can't compare Item to non-Item type")
        return self.views < value.views

    class Meta:
        verbose_name_plural = "Items"
        app_label = "main"
