"""This module defines tests for the Category django model"""

from typing import List

import pytest

from app.tests.mocks import MockItem
from main.models import Category, Item


@pytest.mark.django_db(transaction=True)
class TestItems:
    """Tests for the Item django model"""

    # pylint: disable=no-self-use
    def test_create_item(
        self, mock_default_category: Category, mock_default_item: Item
    ):
        """Tests item created with the expected attributes"""
        # Given: Default field values defined in mock.py
        # When: the mock_default_item fixture is called
        _id = f"{mock_default_category.id}-{MockItem.DEFAULT_ID}"

        attr_mapping = {
            mock_default_item.item_name: f"{MockItem.DEFAULT_ITEM_NAME}{_id}",
            mock_default_item.summary: f"{MockItem.DEFAULT_SUMMARY}{_id}",
            mock_default_item.content: f"{MockItem.DEFAULT_CONTENT}{_id}",
            mock_default_item.date_published: f"{MockItem.DEFAULT_DATE}",
            mock_default_item.category_name: mock_default_category,
        }
        # Then: Item object fields have been assigned correctly
        assert all(
            cat_attr == dummy_var for cat_attr, dummy_var in attr_mapping.items()
        )

    # pylint: disable=no-self-use
    def test_attr_types(self, mock_default_item: Item):
        """Tests item created with the expected attributes types"""
        # Given: Default field values defined in mock.py
        # When: the mock_default_item fixture is called
        type_mapping = {
            mock_default_item.item_name: str,
            mock_default_item.summary: str,
            mock_default_item.content: str,
            mock_default_item.date_published: str,
            mock_default_item.item_slug: str,
            mock_default_item.category_name: Category,
            mock_default_item.views: int,
        }
        # Then: Item object fields have the correct types
        assert all(
            isinstance(attr, attr_type) for attr, attr_type in type_mapping.items()
        )

    # pylint: disable=no-self-use
    def test_item_str_cast(self, mock_default_item: Item):
        """Tests Item str() method is overridden"""
        assert str(mock_default_item) == mock_default_item.item_name

    # pylint: disable=no-self-use
    def test_item_repr_cast(self, mock_default_item: Item):
        """Tests Item repr() method is overridden"""
        assert repr(mock_default_item) == (
            f"Item=(id={mock_default_item.id},item_name="
            f"{mock_default_item.item_name},"
            f"item_slug={mock_default_item.item_slug})"
        )

    # pylint: disable=no-self-use
    def test_load_items(self, load_default_items: List[Item]):
        """Test that load_default_items does insert Item objects in the DB"""
        assert Item.objects.all().count() == len(load_default_items)

    # pylint: disable=no-self-use
    def test_mock_items(self, mock_default_items: List[Item]):
        """
        Test that mock_default_items fixture does return Item objects
        but will not save them into the DB
        """
        assert Item.objects.all().count() == 0
        assert all(isinstance(obj, Item) for obj in mock_default_items)
