"""This module defines tests for the login page"""

from http import HTTPStatus
from typing import Dict
from unittest.mock import Mock

import pytest
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.urls import reverse

from helpers.constants import TemplateNames


@pytest.mark.django_db(transaction=True)
class TestViewLogin:
    """Tests for the login page"""

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_view_login_page(self, client):
        """Test the Login page is rendered with the AuthenticationForm form"""
        # When: GET request on the login page
        response = client.get(reverse("login"))
        # Then: Login page is rendered with 200 and it includes the AuthenticationForm
        assert TemplateNames.LOGIN.value in [t.name for t in response.templates]
        assert response.status_code == HTTPStatus.OK.value
        assert isinstance(response.context["form"], AuthenticationForm)

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_login_invalid_user(
        self, monkeypatch, client, mock_user: User, mock_invalid_user_dict: Dict
    ):
        """Test for when user enters invalid credentials on the login page"""

        # Given a mock authenticate function that returns a valid user
        monkeypatch.setattr(
            "django.contrib.auth.authenticate",
            mock_authenticate := Mock(return_value=mock_user),
        )
        monkeypatch.setattr("main.views.login", mock_login := Mock())

        # When: users attempts to login with invalid credentials
        response = client.post(reverse("login"), data=mock_invalid_user_dict)

        # Then: authenticate and login functions are not called
        mock_authenticate.assert_not_called()
        mock_login.assert_not_called()
        # Then: User stays on the login page with a 200 returned
        assert TemplateNames.LOGIN.value in [t.name for t in response.templates]
        assert response.status_code == HTTPStatus.OK.value

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_login_valid_user(
        self, monkeypatch, client, mock_user: User, mock_user_dict: Dict
    ):
        """Test for when user enters valid credentials on the login page"""
        # Given a mock authenticate function that returns a valid user
        monkeypatch.setattr(
            "main.views.authenticate", mock_authenticate := Mock(return_value=mock_user)
        )
        monkeypatch.setattr("main.views.login", mock_login := Mock())

        # When: users attempts to login with valid credentials
        response = client.post(reverse("login"), data=mock_user_dict)

        # Then: authenticate and login functions are called
        mock_authenticate.assert_called_with(
            username=mock_user_dict.get("username"),
            password=mock_user_dict.get("password"),
        )
        mock_login.assert_called_with(response.wsgi_request, mock_user)
        # Then: No templates are returned and user is redirect to the home page
        assert len(response.templates) == 0
        assert response.status_code == HTTPStatus.FOUND.value
