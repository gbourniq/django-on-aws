import sys
from typing import List

from main.models import Category, Item


class MockCategory:
    """
    Class to create Mock Category objects for testing
    """

    DEFAULT_ID = 1
    DEFAULT_CATEGORY_NAME = "Category "
    DEFAULT_SUMMARY = "summary for category "
    DEFAULT_IMAGE_NAME = "img-url"
    DEFAULT_IMAGE_EXTENSION = "png"
    DEFAULT_CATEGORY_SLUG = "cat-slug-"

    @staticmethod
    def default_category(_id: int = DEFAULT_ID, **kwargs) -> Category:
        """
        Generates a default mock Category object when
        calling MockCategory.default_category().
        
        Distincts Category objects can be created:
        - By providing unique `_id` values.
        - And/or by providing a number of custom kwargs.
        
        Eg.
        custom_category=MockCategory.default_category(
            _id=235,
            category_name="Super Category "
            category_slug="supercat-"
        )
        will generates a Category object with the following
        attributes:
            * id = 235
            * category_name = "Super Category 235"
            * summary = "summary for category 235"
            * image = "img-url-235.png"
            * category_slug = "cat-slug-235"
        """

        category_data = {
            "id": _id,
            "category_name": kwargs.get(
                "category_name", f"{MockCategory.DEFAULT_CATEGORY_NAME}{_id}"
            ),
            "summary": kwargs.get(
                "summary", f"{MockCategory.DEFAULT_SUMMARY}{_id}"
            ),
            "image": kwargs.get(
                "image",
                f"{MockCategory.DEFAULT_IMAGE_NAME}{_id}.{MockCategory.DEFAULT_IMAGE_EXTENSION}",
            ),
            "category_slug": kwargs.get(
                "category_slug", f"{MockCategory.DEFAULT_CATEGORY_SLUG}{_id}"
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
            category_slug="supercat-"
        )
        """

        category_ids = [
            MockCategory.DEFAULT_ID + i for i in range(categories_count)
        ]
        default_categories = [
            MockCategory.default_category(_id, **kwargs)
            for _id in category_ids
            if _id > 0
        ]
        return default_categories


class MockItem:
    """
    Class to create Mock Item objects for testing
    """

    DEFAULT_ID = 1
    DEFAULT_ITEM_NAME = "Item "
    DEFAULT_SUMMARY = "summary for item "
    DEFAULT_CONTENT = "content for item "
    DEFAULT_DATE = "2020-05-22 19:49:50+00:00"
    DEFAULT_ITEM_SLUG = "item-slug-"
    DEFAULT_CATEGORY = MockCategory.DEFAULT_ID

    @staticmethod
    def default_item(
        parent_category: Category, item_id: int = DEFAULT_ID, **kwargs
    ) -> Item:
        """
        Generates a default mock Item object when
        calling MockItem.default_item().
        
        In a similar way as the Category class,
        distincts Item objects can be created:
        - By providing unique `_id` values.
        - And/or by providing a number of custom kwargs.
        
        One thing to note is the `parent_category` argument,
        which is the Category object the Item "belong to".
        
        If the given category object does not exist in the database,
        then the item creation fails with an error message.
        """

        if parent_category.category_name not in [
            cat.category_name for cat in Category.objects.all()
        ]:
            print(
                f"""Parent category {parent_category} does not exist in the databse.\n
                  Please creating it prior to running this function."""
            )
            sys.exit()

        _id = f"{parent_category.id}-{item_id}"

        item_data = {
            "item_name": kwargs.get(
                "item_name", f"{MockItem.DEFAULT_ITEM_NAME}{_id}"
            ),
            "summary": kwargs.get(
                "summary", f"{MockItem.DEFAULT_SUMMARY}{_id}"
            ),
            "content": kwargs.get(
                "content", f"{MockItem.DEFAULT_CONTENT}{_id}"
            ),
            "date_published": kwargs.get(
                "date_published", f"{MockItem.DEFAULT_DATE}",
            ),
            "item_slug": kwargs.get(
                "item_slug", f"{MockItem.DEFAULT_ITEM_SLUG}{_id}"
            ),
            "category_name": parent_category,
        }

        dummy_item = Item.create(item_data)

        return dummy_item

    @staticmethod
    def default_items(
        items_count: int, parent_category: Category, **kwargs
    ) -> List[Item]:
        """
        Generates a list of default items
        """

        item_ids = [MockItem.DEFAULT_ID + i for i in range(items_count)]
        default_items = list(
            map(
                lambda _id: MockItem.default_item(
                    parent_category, _id, **kwargs
                ),
                item_ids,
            )
        )

        return default_items
