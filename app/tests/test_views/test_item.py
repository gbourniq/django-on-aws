"""This module defines tests for the items page"""

from http import HTTPStatus
from typing import List

import pytest
from django.db.models.query import QuerySet
from django.urls import reverse

from helpers.constants import TemplateNames
from main.models import Category, Item


@pytest.mark.django_db(transaction=True)
class TestViewItems:
    """
    Tests for the view items page, which occurs when a user click
    on a category
    """

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_view_items_no_data(self, client):
        """Test view Category page when no category exist in the database"""
        # When: GET request to /cat-slug-1
        response = client.get(
            reverse("items_view", kwargs={"category_slug": "cat-slug-1"},)
        )
        # Then: Users is redirected to go-back-home page and 404 handled
        assert TemplateNames.GO_BACK_HOME.value in [t.name for t in response.templates]
        assert response.status_code == HTTPStatus.OK.value
        assert response.context["code_handled"] == HTTPStatus.NOT_FOUND.value

    @pytest.mark.integration
    # pylint: disable=unused-argument
    # pylint: disable=no-self-use
    def test_view_items_valid_url(self, client, load_default_item: Item):
        """Test that GET /<category>/ are redirected to /<category>/<first_item>/"""
        # When: GET request to /cat-slug-1
        response = client.get(
            reverse("items_view", kwargs={"category_slug": "cat-slug-1"})
        )
        # Then: User redirected to /items/cat-slug-1/
        assert response.request["PATH_INFO"] == "/items/cat-slug-1/"
        assert response.status_code == HTTPStatus.FOUND.value
        assert len(response.templates) == 0

    @pytest.mark.integration
    # pylint: disable=unused-argument
    # pylint: disable=no-self-use
    def test_view_items_invalid_url(self, client, load_default_item: Item):
        """Test that 404 is handled when category_slug path is invalid"""
        # When: GET request to /unknown-cat-slug
        response = client.get(
            reverse("items_view", kwargs={"category_slug": "unknown-cat-slug"})
        )
        # Then: 404 handled and go-back-home template is rendered
        assert response.status_code == HTTPStatus.OK.value
        assert response.context["code_handled"] == HTTPStatus.NOT_FOUND.value
        assert TemplateNames.GO_BACK_HOME.value in [t.name for t in response.templates]


@pytest.mark.django_db(transaction=True)
class TestViewItem:
    """
    Tests for the item details page which occurs when a user click on a
    specific item
    """

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_view_item_no_data(self, client):
        """Test view Item page when no item exist in the database"""
        # GET request to /items/cat-slug-1/item-slug-1-1/ which does not exist
        response = client.get(
            reverse(
                "item_view",
                kwargs={"category_slug": "cat-slug-1", "item_slug": "item-slug-1-1",},
            )
        )
        # Then: go-back-home page rendered and 404 handled
        assert TemplateNames.GO_BACK_HOME.value in [t.name for t in response.templates]
        assert response.status_code == HTTPStatus.OK.value
        assert response.context["code_handled"] == HTTPStatus.NOT_FOUND.value

    @pytest.mark.integration
    def test_view_item_valid_url_single_item(
        # pylint: disable=unused-argument
        # pylint: disable=no-self-use
        self,
        client,
        load_default_item: Item,
    ):
        """Test Item page rendered with a valid GET /<category>/<first_item>/"""
        # Given: GET request to a valid endpoint `/cat-slug-1/item-slug-1-1/`
        response = client.get(
            reverse(
                "item_view",
                kwargs={"category_slug": "cat-slug-1", "item_slug": "item-slug-1-1",},
            )
        )
        # Then: the items template is rendered with the expected context object
        assert response.request["PATH_INFO"] == "/items/cat-slug-1/item-slug-1-1/"
        assert response.status_code == HTTPStatus.OK.value
        assert TemplateNames.ITEMS.value in [t.name for t in response.templates]
        assert isinstance(response.context["item"], Item)
        assert isinstance(response.context["sidebar"], QuerySet)
        assert isinstance(response.context["this_item_idx"], int)
        assert isinstance(response.context["category"], Category)

    @pytest.mark.integration
    @pytest.mark.parametrize("initial_view_count", [0, 2, 5, 10, 100])
    # pylint: disable=no-self-use
    def test_views_incremented(
        self, client, initial_view_count: int, mock_default_item: Item,
    ):
        """Test the views field is incremented when a valid item url is visited."""
        # Given: An initial view count for a given item object
        mock_default_item.views = initial_view_count
        mock_default_item.save()
        # When: GET request the item page
        response = client.get(
            reverse(
                "item_view",
                kwargs={"category_slug": "cat-slug-1", "item_slug": "item-slug-1-1",},
            )
        )
        # Then: item view is incremented
        assert response.request["PATH_INFO"] == "/items/cat-slug-1/item-slug-1-1/"
        assert response.status_code == HTTPStatus.OK.value
        assert TemplateNames.ITEMS.value in [t.name for t in response.templates]
        assert response.context["item"].views == initial_view_count + 1

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "category_slug, item_slug",
        [
            ("invalid-slug", "invalid-slug"),
            ("cat-slug-1", "item-slug-1-2"),
            ("cat-slug-2", "item-slug-1-1"),
        ],
    )
    # pylint: disable=unused-argument
    # pylint: disable=no-self-use
    def test_view_item_invalid_url_single_item(
        self, client, category_slug: str, item_slug: str, load_default_item: Item,
    ):
        """Test 404 in handled with invalid items endpoints are visited"""
        # When: GET Request to an invalid endpoints - (not `/cat-slug-1/item-slug-1-1/`)
        response = client.get(
            reverse(
                "item_view",
                kwargs={"category_slug": category_slug, "item_slug": item_slug,},
            )
        )
        # Then: 404 is handled and go-back-home page rendered
        assert response.status_code == HTTPStatus.OK.value
        assert response.context["code_handled"] == HTTPStatus.NOT_FOUND.value
        assert TemplateNames.GO_BACK_HOME.value in [t.name for t in response.templates]

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "category_slug, item_slug",
        [("cat-slug-1", "item-slug-1-2"), ("cat-slug-1", "item-slug-1-3"),],
    )
    # pylint: disable=no-self-use
    def test_view_item_valid_url_multiple_items(
        self,
        client,
        category_slug: str,
        item_slug: str,
        # pylint: disable=unused-argument
        load_default_items: List[Item],
    ):
        """
        Test the view Item page is rendered with valid /<category>/<first_item>/
        Valid endpoints are: `/cat-slug-<1>/item-slug-<1>-<1:5>/`
        """
        # When: GET request to valid endpoints
        response = client.get(
            reverse(
                "item_view",
                kwargs={"category_slug": category_slug, "item_slug": item_slug,},
            )
        )
        # Then: item view page is rendered with expected context objects
        assert response.request["PATH_INFO"] == f"/items/{category_slug}/{item_slug}/"
        assert response.status_code == HTTPStatus.OK.value
        assert TemplateNames.ITEMS.value in [t.name for t in response.templates]
        assert isinstance(response.context["item"], Item)
        assert isinstance(response.context["sidebar"], QuerySet)
        assert isinstance(response.context["this_item_idx"], int)
        assert isinstance(response.context["category"], Category)

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "category_slug, item_slug",
        [
            ("invalid-slug", "invalid-slug"),
            ("cat-slug-1", "item-slug-1-9"),
            ("cat-slug-2", "item-slug-2-1"),
            ("cat-slug-3", "item-slug-3-1"),
            ("cat-slug-9", "item-slug-1-1"),
        ],
    )
    # pylint: disable=no-self-use
    def test_view_item_invalid_url_multiple_items(
        self,
        client,
        category_slug: str,
        item_slug: str,
        # pylint: disable=unused-argument
        load_default_items: List[Item],
    ):
        """
        Test 404 in handled with invalid /<category>/<first_item>/ endpoints
        Valid endpoints are: `/cat-slug-<1>/item-slug-<1>-<1:5>/`
        """
        # When: GET request to valid endpoints
        response = client.get(
            reverse(
                "item_view",
                kwargs={"category_slug": category_slug, "item_slug": item_slug,},
            )
        )
        # Then: 404 handled and go-back-home page is rendered
        assert response.status_code == HTTPStatus.OK.value
        assert response.context["code_handled"] == HTTPStatus.NOT_FOUND.value
        assert TemplateNames.GO_BACK_HOME.value in [t.name for t in response.templates]

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "category_slug, item_slug",
        [
            ("cat-slug-1", "item-slug-1-4"),
            ("cat-slug-2", "item-slug-2-3"),
            ("cat-slug-3", "item-slug-3-1"),
            ("cat-slug-4", "item-slug-4-5"),
            ("cat-slug-5", "item-slug-5-2"),
        ],
    )
    # pylint: disable=no-self-use
    def test_view_item_valid_url_multiple_categories(
        self,
        client,
        category_slug: str,
        item_slug: str,
        # pylint: disable=unused-argument
        load_default_items_and_cats: List[Item],
    ):
        """
        Test the view Item page is rendered with valid
        /<category>/<first_item>/ endpoints
        Valid endpoints are: `/cat-slug-<1:5>/item-slug-<1:5>-<1:5>/`
        """
        # When: GET request to valid endpoints
        response = client.get(
            reverse(
                "item_view",
                kwargs={"category_slug": category_slug, "item_slug": item_slug,},
            )
        )
        # Then: item view page is rendered with expected context objects
        assert response.request["PATH_INFO"] == f"/items/{category_slug}/{item_slug}/"
        assert response.status_code == HTTPStatus.OK.value
        assert TemplateNames.ITEMS.value in [t.name for t in response.templates]
        assert isinstance(response.context["item"], Item)
        assert isinstance(response.context["sidebar"], QuerySet)
        assert isinstance(response.context["this_item_idx"], int)
        assert isinstance(response.context["category"], Category)

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "category_slug, item_slug",
        [
            ("invalid-slug", "invalid-slug"),
            ("cat-slug-1", "item-slug-1-9"),
            ("cat-slug-2", "item-slug-2-9"),
            ("cat-slug-7", "item-slug-7-1"),
            ("cat-slug-8", "item-slug-8-1"),
        ],
    )
    # pylint: disable=no-self-use
    def test_view_item_invalid_url_multiple_categories(
        self,
        client,
        category_slug: str,
        item_slug: str,
        # pylint: disable=unused-argument
        load_default_items_and_cats: List[Item],
    ):
        """
        Test 404 in handled with invalid /<category>/<first_item>/ endpoints
        Valid endpoints are: `/cat-slug-<1:5>/item-slug-<1:5>-<1:5>/`
        """
        # When: GET request to invalid endpoints
        response = client.get(
            reverse(
                "item_view",
                kwargs={"category_slug": category_slug, "item_slug": item_slug,},
            )
        )
        # Then: 404 handled and go-back-home page is rendered
        assert response.status_code == HTTPStatus.OK.value
        assert response.context["code_handled"] == HTTPStatus.NOT_FOUND.value
        assert TemplateNames.GO_BACK_HOME.value in [t.name for t in response.templates]
