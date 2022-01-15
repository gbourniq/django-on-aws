"""This module defines common objects used across tests"""

from typing import Dict, List
from unittest.mock import Mock

import pytest
from django.contrib.auth.models import User

from app.helpers.constants import THUMBNAIL_SUFFIX
from main.forms import ContactForm
from main.models import Category, Item
from tests.mocks import MockCategory, MockItem, MockUser


def save_mock_category(monkeypatch, category: Category) -> None:
    """
    Mock the resize_image() function to prevent the need of creating and
    processing dummy images when saving Category objects.
    """
    mock_resize_image = Mock(return_value=category.image)
    monkeypatch.setattr(Category, "resize_image", mock_resize_image)
    category.save()
    mock_resize_image.assert_called_once_with(category.image)


def save_mock_item(monkeypatch, item: Item) -> None:
    """
    Mock the resize_image() function to prevent the need of creating and
    processing dummy images when saving Item objects.
    """
    mock_resize_image = Mock(return_value=item.image)
    monkeypatch.setattr(Item, "resize_image", mock_resize_image)
    item.save()
    mock_resize_image.assert_called_once_with(item.image, suffix=THUMBNAIL_SUFFIX)


##########################
#
#   Category Fixtures
#
##########################
@pytest.fixture
def mock_default_category() -> Category:
    """Returns a default category object (unsaved)"""
    return MockCategory.default_category()


@pytest.fixture
def load_default_category(monkeypatch) -> Category:
    """Saves a default category object, and return the object"""
    default_category = MockCategory.default_category()
    save_mock_category(monkeypatch, default_category)
    return default_category


@pytest.fixture
def mock_default_categories() -> List[Category]:
    """Returns a default category objects (unsaved)"""
    return MockCategory.default_categories(categories_count=5)


@pytest.fixture
def load_default_categories(monkeypatch) -> List[Category]:
    """Saves default category objects, and return objects"""
    default_categories = MockCategory.default_categories(categories_count=5)
    for default_category in default_categories:
        save_mock_category(monkeypatch, default_category)
    return default_categories


##########################
#
#   Item Fixtures
#
##########################
@pytest.fixture
def mock_default_item(monkeypatch) -> Item:
    """Return a default item object (unsaved)"""
    default_category = MockCategory.default_category()
    save_mock_category(monkeypatch, default_category)
    return MockItem.default_item(parent_category=default_category)


@pytest.fixture
def load_default_item(monkeypatch) -> Item:
    """Save a default item object, and return the object"""
    default_category = MockCategory.default_category()
    save_mock_category(monkeypatch, default_category)
    default_item = MockItem.default_item(parent_category=default_category)
    save_mock_item(monkeypatch, default_item)
    return mock_default_item


@pytest.fixture
def mock_default_items() -> List[Item]:
    """Return a list of default item objects (unsaved)"""
    return MockItem.default_items(
        items_count=5, parent_category=MockCategory.default_category()
    )


@pytest.fixture
def load_default_items(monkeypatch) -> List[Item]:
    """Save default item objects, and return the objects"""
    default_category = MockCategory.default_category()
    save_mock_category(monkeypatch, default_category)
    default_items = MockItem.default_items(
        items_count=5, parent_category=default_category
    )
    # pylint: disable=expression-not-assigned
    [save_mock_item(monkeypatch, itm) for itm in default_items]
    return default_items


@pytest.fixture
def load_default_items_and_cats(
    monkeypatch, categories_count=5, items_count=5
) -> List[Item]:
    """
    Creates and save a given number of category objects, and for each one,
    it creates/saves a given number of (children) item objects.

    Eg. By setting categories_count=5; and items_count=5;
    This will create and load a total of 5 categories,
    and 25 items into the database.
    """
    created_categories = MockCategory.default_categories(categories_count)
    created_items = []
    for category in created_categories:
        save_mock_category(monkeypatch, category)
        items = MockItem.default_items(items_count, parent_category=category)
        # pylint: disable=expression-not-assigned
        [save_mock_item(monkeypatch, itm) for itm in items]
        created_items.append(items)
    return created_categories, created_items


##########################
#
#   Other Fixtures
#
##########################


@pytest.fixture
def mock_contact_form() -> ContactForm:
    """Fixture for a valid ContactForm"""
    mock_form = ContactForm()
    mock_form.name = "dummy name"
    mock_form.contact_email = "dummy@mail.com"
    mock_form.subject = "dummy subject"
    mock_form.message = "dummy content"
    return mock_form


@pytest.fixture
def mock_user_dict() -> Dict:
    """Fixture to create the default user data"""
    return MockUser.mock_user_data()


@pytest.fixture
def mock_user() -> User:
    """Fixture to create the default user"""
    return MockUser.mock_user_object()


@pytest.fixture
def mock_invalid_user_dict() -> Dict:
    """User credentials which are notsaved in the database"""
    return MockUser.mock_invalid_user_data()


@pytest.fixture
def mock_user_form_dict() -> Dict:
    """Fixture to create a default user form data"""
    return MockUser.mock_user_form_data()
