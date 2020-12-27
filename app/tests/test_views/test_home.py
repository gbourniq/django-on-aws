"""This module defines tests for the home page"""

from http import HTTPStatus

import pytest
from django.urls import reverse

from helpers.constants import TemplateNames


@pytest.mark.django_db(transaction=True)
class TestViewHome:
    """Tests for the home page"""

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_view_homepage(self, client):
        """Test the view home page template is rendered"""
        response = client.get(reverse("home"))
        assert TemplateNames.HOME.value in [t.name for t in response.templates]
        assert response.status_code == HTTPStatus.OK.value
