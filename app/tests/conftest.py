# from unittest.mock import Mock
from typing import Dict, List
from unittest.mock import Mock

import pytest
from django.contrib.auth.models import User

from app.tests.mocks import MockCategory, MockItem
from main.forms import ContactForm
from main.models import Category, Item


def save_mock_category(monkeypatch, category: Category) -> None:
    """
    Mock the resizeImage() function to prevent the need of creating and 
    processing dummy images when saving Category objects.
    """
    mock_resize_image = Mock(return_value=category.image)
    monkeypatch.setattr(Category, "resizeImage", mock_resize_image)
    category.save()
    mock_resize_image.assert_called_once_with(category.image)


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
def load_default_category(
    mock_default_category: Category, monkeypatch
) -> Category:
    """Saves a default category object, and return the object"""
    if mock_default_category not in Category.objects.all():
        save_mock_category(monkeypatch, mock_default_category)
    return mock_default_category


@pytest.fixture
def mock_default_categories() -> List[Category]:
    """Returns a default category objects (unsaved)"""
    return MockCategory.default_categories(categories_count=5)


@pytest.fixture
def load_default_categories(
    mock_default_categories: List[Category], monkeypatch
) -> List[Category]:
    """Saves default category objects, and return objects"""
    for mock_default_category in mock_default_categories:
        if mock_default_category not in Category.objects.all():
            save_mock_category(monkeypatch, mock_default_category)
    return mock_default_categories


##########################
#
#   Item Fixtures
#
##########################
@pytest.fixture
def mock_default_item(load_default_category) -> Item:
    """Return a default item object (unsaved)"""
    return MockItem.default_item(parent_category=load_default_category)


@pytest.fixture
def load_default_item(mock_default_item: Item) -> Item:
    """Save a default item object, and return the object"""
    if mock_default_item not in Item.objects.all():
        mock_default_item.save()
    return mock_default_item


@pytest.fixture
def mock_default_items(load_default_category) -> List[Item]:
    """Return a list of default item objects (unsaved)"""
    return MockItem.default_items(
        items_count=5, parent_category=load_default_category
    )


@pytest.fixture
def load_default_items(mock_default_items: List[Item]) -> List[Item]:
    """Save default item objects, and return the objects"""
    [
        mock_default_item.save()
        for mock_default_item in mock_default_items
        if mock_default_item.item_name not in Item.objects.all()
    ]
    return mock_default_items


@pytest.fixture
def load_default_items_and_categories(
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
        [itm.save() for itm in items]
        created_items.append(items)
    return created_categories, created_items


##########################
#
#   Other Fixtures
#
##########################


@pytest.fixture
def mock_email_host_user(monkeypatch) -> ContactForm:
    mock_email_host_user = Mock(return_value="dummy@email.com")
    monkeypatch.setattr(
        "django.conf.settings.EMAIL_HOST_USER", mock_email_host_user
    )


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
def mock_user_data() -> Dict:
    """Fixture to create the default user data"""
    mock_user_data = {
        "username": "mock_user_data",
        "email": "mydummy@mail.com",
        "password": "dummypass",
    }
    return mock_user_data


@pytest.fixture
def mock_user(mock_user_data) -> Dict:
    """Fixture to create the default user"""
    mock_user = User.objects.create_user(**mock_user_data)
    return mock_user


@pytest.fixture
def mock_user_form_data() -> Dict:
    """Fixture to create a default user form data"""
    mock_user_form_data = {
        "username": "mock_user_form_data",
        "email": "mydummy@mail.com",
        "password1": "dummypass",
        "password2": "dummypass",
    }
    return mock_user_form_data
