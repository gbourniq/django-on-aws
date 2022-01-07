"""
This module defines classes to build mock category
and item objects for unit-tests
"""

from typing import Dict, List

from django.contrib.auth.models import User

from main.models import Category, Item


class MockUser:
    """Class to create Mock User data and objects"""

    @staticmethod
    def mock_user_data() -> Dict:
        """Mock user data"""
        return dict(
            username="mock_user_data", email="mydummy@mail.com", password="dummypass",
        )

    @staticmethod
    def mock_user_object() -> User:
        """Mock User Object"""
        return User.objects.create_user(**MockUser.mock_user_data())

    @staticmethod
    def mock_invalid_user_data() -> Dict:
        """Mock user form data"""
        return dict(username="unknown_user", password="unknown_pass")

    @staticmethod
    def mock_user_form_data() -> Dict:
        """Mock user form data"""
        return dict(
            username="mock_user_form_data",
            email="mydummy@mail.com",
            password1="dummypass",
            password2="dummypass",
        )


class MockCategory:
    """Class to create Mock Category objects for testing"""

    DEFAULT_ID = 1
    DEFAULT_CATEGORY_NAME = "Category "
    DEFAULT_SUMMARY = "summary for category "
    DEFAULT_IMG_NAME = "img-url"
    DEFAULT_IMG_EXT = "png"

    @staticmethod
    def default_category(_id: int = DEFAULT_ID, **kwargs) -> Category:
        """
        Generates a default mock Category object

        Distincts Category objects can be created:
        - By providing unique `_id` values.
        - And/or by providing a number of custom kwargs.

        Eg.
        custom_category=MockCategory.default_category(
            _id=235,
            category_name="Super Category "
        )
        will generates a Category object with the following
        attributes:
            * id = 235
            * category_name = "Super Category 235"
            * summary = "summary for category 235"
            * image = "img-url-235.png"
        """

        category_data = {
            "id": _id,
            "category_name": kwargs.get(
                "category_name", f"{MockCategory.DEFAULT_CATEGORY_NAME}{_id}"
            ),
            "summary": kwargs.get("summary", f"{MockCategory.DEFAULT_SUMMARY}{_id}"),
            "image": kwargs.get(
                "image",
                f"{MockCategory.DEFAULT_IMG_NAME}{_id}.{MockCategory.DEFAULT_IMG_EXT}",
            ),
        }

        dummy_category = Category.create(category_data)

        return dummy_category

    @staticmethod
    def default_categories(categories_count: int, **kwargs) -> List[Category]:
        """
        Generates a list of default mock Category objects.

        In the same way as MockCategory.default_category(),
        the default Category attribute can be overriden.
        Eg.
        custom_categories=MockCategory.default_categories(
            categories_count=5
            category_name="Super Category "
        )
        """

        category_ids = [MockCategory.DEFAULT_ID + i for i in range(categories_count)]
        default_categories = [
            MockCategory.default_category(_id, **kwargs)
            for _id in category_ids
            if _id > 0
        ]
        return default_categories


class MockItem:
    """Class to create Mock Item objects for testing"""

    DEFAULT_ID = 1
    DEFAULT_ITEM_NAME = "Item "
    DEFAULT_SUMMARY = "summary for item "
    DEFAULT_IMG_NAME = "img-url"
    DEFAULT_IMG_EXT = "png"
    DEFAULT_CONTENT = "content for item "
    DEFAULT_DATE = "2020-05-22 19:49:50+00:00"
    DEFAULT_CATEGORY = MockCategory.DEFAULT_ID

    @staticmethod
    def default_item(
        parent_category: Category, item_id: int = DEFAULT_ID, **kwargs
    ) -> Item:
        """
        Generates a default mock Item object

        Distinct Item objects can be created:
        - By providing unique `_id` values.
        - And/or by providing a number of custom kwargs.

        One thing to note is the `parent_category` argument,
        which is the Category object the Item "belong to".
        """
        assert (
            Category.objects.filter(category_name=parent_category.category_name)
            is not None
        ), f"Parent category {parent_category} does not exist in the databse."

        _id = f"{parent_category.id}-{item_id}"

        item_data = {
            "item_name": kwargs.get("item_name", f"{MockItem.DEFAULT_ITEM_NAME}{_id}"),
            "summary": kwargs.get("summary", f"{MockItem.DEFAULT_SUMMARY}{_id}"),
            "image": kwargs.get(
                "image",
                f"{MockCategory.DEFAULT_IMG_NAME}{_id}.{MockCategory.DEFAULT_IMG_EXT}",
            ),
            "content": kwargs.get("content", f"{MockItem.DEFAULT_CONTENT}{_id}"),
            "date_published": kwargs.get("date_published", f"{MockItem.DEFAULT_DATE}",),
            "category_name": parent_category,
        }

        dummy_item = Item.create(item_data)

        return dummy_item

    @staticmethod
    def default_items(
        items_count: int, parent_category: Category, **kwargs
    ) -> List[Item]:
        """Generates a list of default items"""

        item_ids = [MockItem.DEFAULT_ID + i for i in range(items_count)]
        default_items = list(
            map(
                lambda _id: MockItem.default_item(parent_category, _id, **kwargs),
                item_ids,
            )
        )

        return default_items
