"""This module defines tests for the login page"""

from unittest.mock import Mock

import pytest
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse


@pytest.mark.django_db(transaction=True)
class TestViewLogin:
    """Tests for the login page"""

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_view_login_page(self, client):
        """
        Test the Login page is rendered with the AuthenticationForm form (GET)
        """

        response = client.get(reverse("login"))

        assert "main/login.html" in [t.name for t in response.templates]
        assert response.status_code == 200
        assert isinstance(response.context["form"], AuthenticationForm)

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_login_invalid_user(
        self, monkeypatch, client, mock_user, mock_invalid_user_dict
    ):
        """
        Tests that authenticate and login functions are not called
        Tests it renders the same login.html page
        """

        mock_authenticate = Mock(return_value=mock_user)
        monkeypatch.setattr("django.contrib.auth.authenticate", mock_authenticate)
        mock_login = Mock()
        monkeypatch.setattr("main.views.login", mock_login)

        response = client.post(reverse("login"), data=mock_invalid_user_dict)

        mock_authenticate.assert_not_called()
        mock_login.assert_not_called()

        assert "main/login.html" in [t.name for t in response.templates]
        assert response.status_code == 200

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_login_valid_user(self, monkeypatch, client, mock_user, mock_user_dict):
        """
        Tests that authenticate and login functions are called
        Tests the redirection to the home page
        """

        mock_valid_user = {
            "username": mock_user_dict.get("username"),
            "password": mock_user_dict.get("password"),
        }

        mock_authenticate = Mock(return_value=mock_user)
        monkeypatch.setattr("main.views.authenticate", mock_authenticate)
        mock_login = Mock()
        monkeypatch.setattr("main.views.login", mock_login)

        response = client.post(reverse("login"), data=mock_valid_user)

        mock_authenticate.assert_called_with(
            username=mock_user_dict.get("username"),
            password=mock_user_dict.get("password"),
        )

        mock_login.assert_called_with(response.wsgi_request, mock_user)

        assert len(response.templates) == 0
        assert response.status_code == 302
