"""This module defines tests manipulating category objects from main.views"""
from http import HTTPStatus

import pytest
from django.db.models.query import QuerySet
from django.urls import reverse

from helpers.constants import TemplateNames


@pytest.mark.django_db(transaction=True)
class TestViewCategory:
    """Tests for the category page"""

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_404_no_category_in_db(self, client):
        """Test that 404 is handled when no category exist"""
        # When: GET request on the view category page when no category exist
        response = client.get(reverse("categories_view"))
        # Then: User redirect to the go-back-home template, with a 200
        assert TemplateNames.GO_BACK_HOME.value in [t.name for t in response.templates]
        assert response.status_code == HTTPStatus.OK.value
        assert response.context["code_handled"] == HTTPStatus.NOT_FOUND.value

    @pytest.mark.integration
    # pylint: disable=unused-argument
    # pylint: disable=no-self-use
    def test_view_category(self, client, load_default_category):
        """Test the Category page when database contains one category object"""
        # When: GET request on the view category page when a category DOES exist
        response = client.get(reverse("categories_view"))
        # Then: Category page template is rendered with the list of categories
        assert TemplateNames.CATEGORIES.value in [t.name for t in response.templates]
        assert response.status_code == HTTPStatus.OK.value
        assert isinstance(response.context["all_categories_list"], QuerySet)
