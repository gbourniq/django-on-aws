from typing import List

import pytest
from django.db.models.query import QuerySet
from django.urls import reverse

from main.models import Category, Item


@pytest.mark.django_db(transaction=True)
class TestViewItems:
    @pytest.mark.integration
    def test_view_items_no_data(self, client):
        """
        Test that 404 is handled when no Category object exist in the database
        """

        response = client.get(
            reverse("items_view", kwargs={"category_slug": "cat-slug-1"},)
        )

        assert "main/go_back_home.html" in (t.name for t in response.templates)
        assert response.status_code == 200
        assert response.context["code_handled"] == 404

    @pytest.mark.integration
    def test_view_items_valid_url(self, client, load_default_item: Item):
        """
        Test that requests to /<category>/ are redirected to /<category>/<first_item>/
        """

        response = client.get(
            reverse("items_view", kwargs={"category_slug": "cat-slug-1"})
        )

        assert response.request["PATH_INFO"] == "/items/cat-slug-1/"
        assert response.status_code == 302
        assert len(response.templates) == 0

    @pytest.mark.integration
    def test_view_items_invalid_url(self, client, load_default_item: Item):
        """
        Test that 404 is handled when category_slug does not correspond to any Category
        """

        response = client.get(
            reverse("items_view", kwargs={"category_slug": "unknown-cat-slug"})
        )

        assert response.status_code == 200
        assert response.context["code_handled"] == 404
        assert "main/go_back_home.html" in (t.name for t in response.templates)


@pytest.mark.django_db(transaction=True)
class TestViewItem:
    @pytest.mark.integration
    def test_view_item_no_data(self, client):
        """
        Test that 404 is handled when no Item object exists in the database
        No endpoints are available because no category/item exists
        """

        response = client.get(
            reverse(
                "item_view",
                kwargs={
                    "category_slug": "cat-slug-1",
                    "item_slug": "item-slug-1-1",
                },
            )
        )

        assert "main/go_back_home.html" in (t.name for t in response.templates)
        assert response.status_code == 200
        assert response.context["code_handled"] == 404

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "category_slug, item_slug", [("cat-slug-1", "item-slug-1-1"),],
    )
    def test_view_item_valid_url_single_item(
        self,
        client,
        category_slug: str,
        item_slug: str,
        load_default_item: Item,
    ):
        """
        Test the view Item page is rendered with a valid /<category>/<first_item>/ endpoint
        Valid endpoints are: `/cat-slug-1/item-slug-1-1/`
        """

        response = client.get(
            reverse(
                "item_view",
                kwargs={
                    "category_slug": category_slug,
                    "item_slug": item_slug,
                },
            )
        )

        assert (
            response.request["PATH_INFO"]
            == f"/items/{category_slug}/{item_slug}/"
        )
        assert response.status_code == 200
        assert "main/items.html" in (t.name for t in response.templates)
        assert isinstance(response.context["item"], Item)
        assert isinstance(response.context["sidebar"], QuerySet)
        assert isinstance(response.context["this_item_idx"], int)
        assert isinstance(response.context["category"], Category)

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "initial_view_count", [0, 2, 5, 10, 100, 1000],
    )
    def test_views_incremented(
        self, client, initial_view_count: int, mock_default_item: Item,
    ):
        """
        Test the views field is incremented when a valid item url is visited.
        """
        mock_default_item.views = initial_view_count
        mock_default_item.save()

        response = client.get(
            reverse(
                "item_view",
                kwargs={
                    "category_slug": "cat-slug-1",
                    "item_slug": "item-slug-1-1",
                },
            )
        )

        assert (
            response.request["PATH_INFO"] == f"/items/cat-slug-1/item-slug-1-1/"
        )
        assert response.status_code == 200
        assert "main/items.html" in (t.name for t in response.templates)
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
    def test_view_item_invalid_url_single_item(
        self,
        client,
        category_slug: str,
        item_slug: str,
        load_default_item: Item,
    ):
        """
        Test 404 in handled with invalid /<category>/<first_item>/ endpoints
        Valid endpoints are: `/cat-slug-1/item-slug-1-1/`
        """

        response = client.get(
            reverse(
                "item_view",
                kwargs={
                    "category_slug": category_slug,
                    "item_slug": item_slug,
                },
            )
        )

        assert response.status_code == 200
        assert response.context["code_handled"] == 404
        assert "main/go_back_home.html" in (t.name for t in response.templates)

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "category_slug, item_slug",
        [("cat-slug-1", "item-slug-1-2"), ("cat-slug-1", "item-slug-1-3"),],
    )
    def test_view_item_valid_url_multiple_items(
        self,
        client,
        category_slug: str,
        item_slug: str,
        load_default_items: List[Item],
    ):
        """
        Test the view Item page is rendered with valid /<category>/<first_item>/ endpoints
        Valid endpoints are: `/cat-slug-<1>/item-slug-<1>-<1:5>/`
        """

        response = client.get(
            reverse(
                "item_view",
                kwargs={
                    "category_slug": category_slug,
                    "item_slug": item_slug,
                },
            )
        )

        assert (
            response.request["PATH_INFO"]
            == f"/items/{category_slug}/{item_slug}/"
        )
        assert response.status_code == 200
        assert "main/items.html" in (t.name for t in response.templates)
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
    def test_view_item_invalid_url_multiple_items(
        self,
        client,
        category_slug: str,
        item_slug: str,
        load_default_items: List[Item],
    ):
        """
        Test 404 in handled with invalid /<category>/<first_item>/ endpoints
        Valid endpoints are: `/cat-slug-<1>/item-slug-<1>-<1:5>/`
        """

        response = client.get(
            reverse(
                "item_view",
                kwargs={
                    "category_slug": category_slug,
                    "item_slug": item_slug,
                },
            )
        )

        assert response.status_code == 200
        assert response.context["code_handled"] == 404
        assert "main/go_back_home.html" in (t.name for t in response.templates)

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
    def test_view_item_valid_url_multiple_categories(
        self,
        client,
        category_slug: str,
        item_slug: str,
        load_default_items_and_categories: List[Item],
    ):
        """
        Test the view Item page is rendered with valid /<category>/<first_item>/ endpoints
        Valid endpoints are: `/cat-slug-<1:5>/item-slug-<1:5>-<1:5>/`
        """

        response = client.get(
            reverse(
                "item_view",
                kwargs={
                    "category_slug": category_slug,
                    "item_slug": item_slug,
                },
            )
        )

        assert (
            response.request["PATH_INFO"]
            == f"/items/{category_slug}/{item_slug}/"
        )
        assert response.status_code == 200
        assert "main/items.html" in (t.name for t in response.templates)
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
    def test_view_item_invalid_url_multiple_categories(
        self,
        client,
        category_slug: str,
        item_slug: str,
        load_default_items_and_categories: List[Item],
    ):
        """
        Test 404 in handled with invalid /<category>/<first_item>/ endpoints
        Valid endpoints are: `/cat-slug-<1:5>/item-slug-<1:5>-<1:5>/`
        """

        response = client.get(
            reverse(
                "item_view",
                kwargs={
                    "category_slug": category_slug,
                    "item_slug": item_slug,
                },
            )
        )

        assert response.status_code == 200
        assert response.context["code_handled"] == 404
        assert "main/go_back_home.html" in (t.name for t in response.templates)
