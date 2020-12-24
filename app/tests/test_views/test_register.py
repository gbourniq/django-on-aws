from unittest.mock import Mock

import pytest
from django.urls import reverse

from main.forms import NewUserForm


@pytest.mark.django_db(transaction=True)
class TestViewRegister:
    @pytest.mark.integration
    def test_view_register_page(self, client):
        """
        Test the Sign up page is rendered with the NewUserForm form (GET)
        """

        response = client.get(reverse("register"))

        assert "main/register.html" in (t.name for t in response.templates)
        assert response.status_code == 200
        assert isinstance(response.context["form"], NewUserForm)

    @pytest.mark.integration
    def test_post_invalid_user(self, monkeypatch, client, mock_user):
        """
        Tests that authenticate and login functions are not called
        Tests it renders the same login.html page
        """

        mock_invalid_user = {
            "username": "unknown_user",
            "password": "unknown_pass",
        }

        mock_authenticate = Mock(return_value=mock_user)
        monkeypatch.setattr(
            "django.contrib.auth.authenticate", mock_authenticate
        )
        mock_login = Mock()
        monkeypatch.setattr("main.views.login", mock_login)

        response = client.post(reverse("login"), data=mock_invalid_user)

        mock_authenticate.assert_not_called()
        mock_login.assert_not_called()

        assert "main/login.html" in (t.name for t in response.templates)
        assert response.status_code == 200

    @pytest.mark.integration
    def test_register_with_valid_form(
        self, monkeypatch, client, mock_user_form_data, mock_user
    ):
        """
        Tests that authenticate and login functions are called
        Tests the redirection to the home page
        """

        mock_login = Mock()
        monkeypatch.setattr("main.views.login", mock_login)
        mock_save_form = Mock(return_value=mock_user)
        monkeypatch.setattr(NewUserForm, "save", mock_save_form)

        response = client.post(reverse("register"), data=mock_user_form_data)

        mock_save_form.assert_called()
        mock_login.assert_called()

        assert len(response.templates) == 0
        assert response.status_code == 302

    @pytest.mark.integration
    def test_register_with_invalid_form(self, monkeypatch, client, mock_user):
        """
        Tests that authenticate and login functions are not called
        Tests the rendering of the same register.html page
        """

        mock_user_form_invalid_data = {
            "username": "",
            "email": "invalid_email",
            "password1": "invalidpass",
            "password2": "invalidpass_not_matching",
        }

        mock_login = Mock()
        monkeypatch.setattr("main.views.login", mock_login)
        mock_save_form = Mock(return_value=mock_user)
        monkeypatch.setattr(NewUserForm, "save", mock_save_form)

        response = client.post(
            reverse("register"), data=mock_user_form_invalid_data
        )

        mock_save_form.assert_not_called()
        mock_login.assert_not_called()

        assert "main/register.html" in (t.name for t in response.templates)
        assert response.status_code == 200

    @pytest.mark.integration
    def test_register_with_existing_user_conflict(
        self, monkeypatch, client, mock_user, mock_user_data
    ):
        """
        Tests that authenticate and login functions are not called
        Tests the rendering of the same register.html page
        """

        # username conflicting with existing mock_user
        mock_user_form_valid_data = {
            "username": mock_user_data.get("username"),
            "email": "mydummy@mail.com",
            "password1": "dummypass",
            "password2": "dummypass",
        }

        mock_login = Mock()
        monkeypatch.setattr("main.views.login", mock_login)
        mock_save_form = Mock(return_value=mock_user)
        monkeypatch.setattr(NewUserForm, "save", mock_save_form)

        response = client.post(
            reverse("register"), data=mock_user_form_valid_data
        )

        mock_save_form.assert_not_called()
        mock_login.assert_not_called()

        assert "main/register.html" in (t.name for t in response.templates)
        assert response.status_code == 200
