"""This module defines tests for the logout page"""

from http import HTTPStatus
from unittest.mock import Mock

import pytest
from django.urls import reverse


@pytest.mark.django_db(transaction=True)
class TestViewLogout:
    """Tests for the logout page"""

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_click_logout_button(self, monkeypatch, client):
        """Test for when user click the logout button"""
        # Given: mock logout function
        monkeypatch.setattr("main.views.logout", mock_logout := Mock())
        # When: GET request to the logout page
        response = client.get(reverse("logout"))
        # Then: mock logout is called
        mock_logout.assert_called_with(response.wsgi_request)
        # Then: No templates returned and user redirected
        assert len(response.templates) == 0
        assert response.status_code == HTTPStatus.FOUND.value
