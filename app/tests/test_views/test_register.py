"""This module defines tests for the register page"""

from http import HTTPStatus
from typing import Dict
from unittest.mock import Mock

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from helpers.constants import TemplateNames
from main.forms import NewUserForm


@pytest.mark.django_db(transaction=True)
class TestViewRegister:
    """Tests for the register page"""

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_get_register_page(self, client):
        """Test for when a user attempts to register"""
        # When: GET request on the register page
        response = client.get(reverse("register"))
        # Then: the register template is rendered with the NewUserForm form
        assert TemplateNames.REGISTER.value in [t.name for t in response.templates]
        assert response.status_code == HTTPStatus.OK.value
        assert isinstance(response.context["form"], NewUserForm)

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_register_with_valid_form(
        self, monkeypatch, client, mock_user_form_dict: Dict
    ):
        """Tests for when user register successfully"""
        # Given: a mock login function
        monkeypatch.setattr("main.views.login", mock_login := Mock())
        # When: user register with valid data
        response = client.post(reverse("register"), data=mock_user_form_dict)
        # Then: the login function is called
        mock_login.assert_called()
        assert len(response.templates) == 0
        assert response.status_code == HTTPStatus.FOUND.value

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_register_with_invalid_form(self, monkeypatch, client, mock_user: User):
        """Tests for when user attempts to register with invalid form data"""
        # Given: invalid register form data
        mock_user_form_invalid_data = {
            "username": "",
            "email": "invalid_email",
            "password1": "invalidpass",
            "password2": "invalidpass_not_matching",
        }
        # Given: mock login function and some user is registered
        monkeypatch.setattr("main.views.login", mock_login := Mock())
        monkeypatch.setattr(
            NewUserForm, "save", mock_save_form := Mock(return_value=mock_user)
        )
        # When: POST the invalid form data on the register page
        response = client.post(reverse("register"), data=mock_user_form_invalid_data)
        # Then: User is not saved through the form, and login function not called
        mock_save_form.assert_not_called()
        mock_login.assert_not_called()
        # Then: User stays on the register page
        assert TemplateNames.REGISTER.value in [t.name for t in response.templates]
        assert response.status_code == HTTPStatus.OK.value

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_register_with_existing_user_conflict(
        self, monkeypatch, client, mock_user: User, mock_user_dict: Dict
    ):
        """Tests for when registering with existing user details"""
        # Given: Form data where username conflicts with existing mock_user
        # Given: mock login function and some user is registered
        monkeypatch.setattr("main.views.login", mock_login := Mock())
        monkeypatch.setattr(
            NewUserForm, "save", mock_save_form := Mock(return_value=mock_user)
        )
        # When: POST user form data of a user that already exists
        response = client.post(reverse("register"), data=mock_user_dict)
        # Then: User is not saved through the form, and login function not called
        mock_save_form.assert_not_called()
        mock_login.assert_not_called()
        assert TemplateNames.REGISTER.value in [t.name for t in response.templates]
        assert response.status_code == HTTPStatus.OK.value
