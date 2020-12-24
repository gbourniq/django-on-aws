from unittest.mock import Mock

import pytest
from django.urls import reverse

from main.forms import ContactForm


@pytest.mark.django_db(transaction=True)
class TestViewContactUs:
    @pytest.mark.integration
    def test_view_contact_us_page(self, client):
        """
        Test the view Category us page is rendered with the Contact Form
        """

        response = client.get(reverse("contact_us"))

        assert "main/contact_us.html" in (t.name for t in response.templates)
        assert response.status_code == 200
        assert isinstance(response.context["form"], ContactForm)

    @pytest.mark.integration
    def test_post_valid_form(
        self, monkeypatch, client, mock_contact_form: ContactForm
    ):
        """
        Test the `Go Back Home` page is rendered when user submit valid form
        and that send_mail is called when a valid form is posted
        """

        mock_send_mail = Mock()
        monkeypatch.setattr("main.views.send_mail", mock_send_mail)

        response = client.post(
            reverse("contact_us"), data=mock_contact_form.json()
        )

        mock_send_mail.assert_called()
        assert "main/go_back_home.html" in (t.name for t in response.templates)
        assert response.status_code == 200

    @pytest.mark.integration
    def test_post_empty_form(self, monkeypatch, client):
        """
        Ensure that, when a user submits an empty form:
        - Redirect to the current page
        - Email function not called
        """

        mock_send_mail = Mock()
        monkeypatch.setattr("main.views.send_mail", mock_send_mail)

        contact_us_url = reverse("contact_us")
        response = client.post(
            contact_us_url, data={}, HTTP_REFERER=contact_us_url
        )

        mock_send_mail.assert_not_called()

        assert "main/contact_us.html" in (t.name for t in response.templates)
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
    def test_post_invalid_form(
        self,
        monkeypatch,
        client,
        name: str,
        contact_email: str,
        subject: str,
        message: str,
    ):
        """
        When invalid forms are submitted, ensures we have a page rediction
        (return code 302) and that the email function is not called,
        """

        mock_send_mail = Mock()
        monkeypatch.setattr("main.views.send_mail", mock_send_mail)

        invalid_form = ContactForm()
        invalid_form.name = name
        invalid_form.contact_email = contact_email
        invalid_form.subject = subject
        invalid_form.message = message

        contact_us_url = reverse("contact_us")
        response = client.post(
            contact_us_url,
            data=invalid_form.json(),
            HTTP_REFERER=contact_us_url,
        )

        mock_send_mail.assert_not_called()

        assert "main/contact_us.html" in (t.name for t in response.templates)
        assert response.status_code == 200
