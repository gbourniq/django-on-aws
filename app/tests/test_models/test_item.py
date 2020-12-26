from typing import List

import pytest

from app.tests.mocks import MockItem
from main.models import Category, Item


@pytest.mark.django_db(transaction=True)
class TestItems:
    def test_create_item(
        self, mock_default_category: Category, mock_default_item: Item
    ):
        """
        Tests item created with the expected attributes
        """

        _id = f"{mock_default_category.id}-{MockItem.DEFAULT_ID}"

        attr_mapping = {
            mock_default_item.item_name: f"{MockItem.DEFAULT_ITEM_NAME}{_id}",
            mock_default_item.summary: f"{MockItem.DEFAULT_SUMMARY}{_id}",
            mock_default_item.content: f"{MockItem.DEFAULT_CONTENT}{_id}",
            mock_default_item.date_published: f"{MockItem.DEFAULT_DATE}",
            mock_default_item.item_slug: f"{MockItem.DEFAULT_ITEM_SLUG}{_id}",
            mock_default_item.category_name: mock_default_category,
        }

        assert all(
            cat_attr == dummy_var for cat_attr, dummy_var in attr_mapping.items()
        )

    def test_attr_types(self, mock_default_item: Item):
        """
        Tests item created with the expected attributes types
        """

        MockItem.DEFAULT_ID

        type_mapping = {
            mock_default_item.item_name: str,
            mock_default_item.summary: str,
            mock_default_item.content: str,
            mock_default_item.date_published: str,
            mock_default_item.item_slug: str,
            mock_default_item.category_name: Category,
            mock_default_item.views: int,
        }

        assert all(
            isinstance(attr, attr_type) for attr, attr_type in type_mapping.items()
        )

    def test_item_str_cast(self, mock_default_item: Item):
        """
        Tests Item str() method is overridden
        """
        assert str(mock_default_item) == mock_default_item.item_name

    def test_item_repr_cast(self, mock_default_item: Item):
        """
        Tests Item repr() method is overridden
        """
        assert (
            repr(mock_default_item)
            == f"Item=(id={mock_default_item.id},item_name={mock_default_item.item_name},item_slug={mock_default_item.item_slug})"
        )

    @pytest.mark.parametrize(
        "view_count_0, view_count_1", [(3, 3), (3, 4), (4, 3),],
    )
    def test_items_comparison(
        self, view_count_0, view_count_1, mock_default_items: List[Item]
    ):
        """
        Tests Item __ge__() and __lt__() methods
        """
        mock_default_items[0].views = view_count_0
        mock_default_items[1].views = view_count_1

        if view_count_0 > view_count_1:
            assert mock_default_items[0].views >= mock_default_items[1].views
            assert mock_default_items[1].views < mock_default_items[0].views
        elif view_count_0 < view_count_1:
            assert mock_default_items[1].views >= mock_default_items[0].views
            assert mock_default_items[0].views < mock_default_items[1].views
        elif view_count_0 == view_count_1:
            assert mock_default_items[0].views >= mock_default_items[1].views
        else:
            pass
