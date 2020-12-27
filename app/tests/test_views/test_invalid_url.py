"""This module defines tests for when invalid url paths are hit"""

from http import HTTPStatus

import pytest
from django.urls import reverse

from helpers import strings
from helpers.constants import TemplateNames


class TestInvalidUrl:
    """Tests for unmatched url paths"""

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_invalid_url(self, client):
        """Tests that invalid url paths are handled"""
        # When: No url match
        response = client.get(reverse("error404"))
        # Then: Handled and returned 200 with a friendly error message
        assert response.status_code == HTTPStatus.OK.value
        assert response.context["code_handled"] == HTTPStatus.NOT_FOUND.value
        assert response.context["message"] == strings.MSG_404
        assert TemplateNames.GO_BACK_HOME.value in [t.name for t in response.templates]
