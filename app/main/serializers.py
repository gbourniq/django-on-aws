# """This module defines serialiazers for the django rest framework api views"""

# from django.utils import timezone
# from rest_framework import serializers

# from main.models import Category, Item


# class CategorySerializer(serializers.ModelSerializer):
#     """
#     Class to serialize Category model.
#     Adding child_items SerializeMethod to display
#     Category child elements (Items)
#     """

#     category_name = serializers.CharField(
#         min_length=0,
#         max_length=20,
#         style={"input_type": "text", "placeholder": "My Category Name"},
#     )
#     summary = serializers.CharField(
#         min_length=2,
#         max_length=200,
#         style={"input_type": "text", "placeholder": "My category summary"},
#     )
#     image = serializers.ImageField(required=False)
#     category_slug = serializers.CharField(
#         style={"input_type": "text", "placeholder": "url-slug-to-category"},
#         help_text="URL slug to redirect to your category. No space allowed!",
#     )
#     child_items = serializers.SerializerMethodField()

#     class Meta:
#         model = Category
#         fields = (
#             "id",
#             "category_name",
#             "summary",
#             "image",
#             "category_slug",
#             "child_items",
#         )

#     def get_child_items(self, instance):
#         """
#         SerializerMethod to return a list of serialized model instances
#         (many=True)
#         """
#         items = Item.objects.filter(category_name=instance)
#         return ItemSerializer(items, many=True).data

#     # def to_representation(self, instance):
#     #     return super().to_representation(instance)


# class ItemSerializer(serializers.ModelSerializer):
#     """Class to serialize Item model"""

#     item_name = serializers.CharField(
#         min_length=0,
#         max_length=20,
#         style={"input_type": "text", "placeholder": "My Item Name"},
#     )
#     summary = serializers.CharField(
#         min_length=2,
#         max_length=200,
#         style={"input_type": "text", "placeholder": "My item summary"},
#     )
#     content = serializers.CharField(
#         min_length=10,
#         style={"input_type": "text", "placeholder": "Write item content here...",},
#         help_text="Use the django admin page to insert formatted text",
#     )
#     date_published = serializers.DateTimeField(
#         default=timezone.now,
#         help_text="Leave blank for current datetime",
#     )
#     item_slug = serializers.CharField(
#         style={"input_type": "text", "placeholder": "url-slug-to-item"},
#         help_text="URL slug to redirect to your item. No space allowed!",
#     )
#     views = serializers.IntegerField(read_only=True)

#     class Meta:
#         model = Item
#         fields = (
#             "id",
#             "item_name",
#             "summary",
#             "content",
#             "date_published",
#             "item_slug",
#             "category_name",
#             "views",
#         )


# # pylint: disable=abstract-method
# class StatSerializer(serializers.Serializer):
#     """Class to serialize CategoryStats"""

#     stats = serializers.DictField(child=serializers.IntegerField())
