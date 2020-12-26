"""This module defines tests for the contact us page"""

import pytest
from django.conf import settings
from django.urls import reverse

from main.forms import ContactForm


@pytest.mark.django_db(transaction=True)
class TestViewContactUs:
    """Tests for the contact us page"""

    @pytest.mark.integration
    @pytest.mark.parametrize("login_required", [True, False])
    # pylint: disable=no-self-use
    def test_view_contact_us_page(self, client, monkeypatch, login_required):
        """
        Test the view Category us page is rendered with the Contact Form
        only if ENABLE_LOGIN_REQUIRED_MIXIN set to False, or user is logged in
        """
        monkeypatch.setattr(
            settings,
            "ENABLE_LOGIN_REQUIRED_MIXIN",
            mock_login_required := login_required,
        )

        response = client.get(reverse("contact_us"))

        if mock_login_required:
            assert not [t.name for t in response.templates]
            assert response.status_code == 302
        else:
            assert "main/contact_us.html" in [t.name for t in response.templates]
            assert response.status_code == 200
            assert isinstance(response.context["form"], ContactForm)

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_post_valid_form(self, client, mock_contact_form: ContactForm):
        """
        Test the `Go Back Home` page is rendered when user submit valid form
        """

        response = client.post(reverse("contact_us"), data=mock_contact_form.json())

        assert "main/go_back_home.html" in [t.name for t in response.templates]
        assert response.status_code == 200

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_post_empty_form(self, client):
        """
        Ensure that, when a user submits an empty form:
        - Redirect to the current page
        """
        contact_us_url = reverse("contact_us")
        response = client.post(contact_us_url, data={}, HTTP_REFERER=contact_us_url)

        assert "main/contact_us.html" in [t.name for t in response.templates]
        assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "name, contact_email, subject, message",
        [
            ("", "valid@email.com", "valid subject", "valid message"),
            ("valid name", "invalid email", "valid subject", "valid message"),
            ("valid name", "", "valid subject", "valid message"),
            ("valid name", "valid@email.com", "", "valid message"),
            ("valid name", "valid@email.com", "valid subject", ""),
        ],
    )
    # pylint: disable=no-self-use
    # pylint: disable=too-many-arguments
    def test_post_invalid_form(
        self, client, name: str, contact_email: str, subject: str, message: str,
    ):
        """
        When invalid forms are submitted, ensures we have a page rediction
        (return code 302)
        """
        invalid_form = ContactForm()
        invalid_form.name = name
        invalid_form.contact_email = contact_email
        invalid_form.subject = subject
        invalid_form.message = message

        contact_us_url = reverse("contact_us")
        response = client.post(
            contact_us_url, data=invalid_form.json(), HTTP_REFERER=contact_us_url,
        )

        assert "main/contact_us.html" in [t.name for t in response.templates]
        assert response.status_code == 200
