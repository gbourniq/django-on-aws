"""This module defines tests for the contact us page"""

import json
from http import HTTPStatus
from unittest.mock import Mock

import pytest
from django.conf import settings
from django.urls import reverse

from helpers.constants import TemplateNames
from main.forms import ContactForm


@pytest.mark.django_db(transaction=True)
class TestViewContactUs:
    """Tests for the contact us page"""

    @pytest.mark.integration
    @pytest.mark.parametrize("login_required", [True, False])
    # pylint: disable=no-self-use
    def test_view_contact_us_page(self, client, monkeypatch, login_required: bool):
        """
        Test the view Category us page is rendered with the Contact Form
        only if ENABLE_LOGIN_REQUIRED_MIXIN set to False, or user is logged in
        """
        # Given: ENABLE_LOGIN_REQUIRED_MIXIN set to True/False
        monkeypatch.setattr(
            settings, "ENABLE_LOGIN_REQUIRED_MIXIN", login_required,
        )
        # When: A GET request to the contact us page
        response = client.get(reverse("contact_us"))
        rendered_templates = [t.name for t in response.templates]
        if login_required:
            # Then: No templates rendered and returns 302
            assert not rendered_templates
            assert response.status_code == HTTPStatus.FOUND.value
        else:
            # Then: contact_us template is rendered with 200
            assert TemplateNames.CONTACT_US.value in rendered_templates
            assert response.status_code == HTTPStatus.OK.value
            assert isinstance(response.context["form"], ContactForm)

    @pytest.mark.integration
    @pytest.mark.parametrize("sns_topic_arn", ["mock_sns_topic_arn", ""])
    # pylint: disable=no-self-use
    def test_post_valid_form(
        self, monkeypatch, client, mock_contact_form: ContactForm, sns_topic_arn: str
    ):
        """Test the `Go Back Home` page is rendered when user submit valid form"""
        # Given: Whether SNS_TOPIC_ARN is set or not
        monkeypatch.setattr(
            settings, "SNS_TOPIC_ARN", sns_topic_arn,
        )
        # Given: mock sns service client
        monkeypatch.setattr("boto3.client", mock_sns_client := Mock())
        # When: POST request on the contact-us page
        response = client.post(reverse("contact_us"), data=mock_contact_form.json())
        if sns_topic_arn:
            # Given: SNS_TOPIC_ARN is set
            # Then: `go-back-home` template is rendered
            assert TemplateNames.GO_BACK_HOME.value in [
                t.name for t in response.templates
            ]
            assert response.status_code == HTTPStatus.OK.value
            # Then: SNS client called with expected parameters
            mock_sns_client("sns").publish.assert_called_once_with(
                TargetArn="mock_sns_topic_arn",
                Message=json.dumps({"default": mock_contact_form.json()}),
            )
        else:
            # Given: SNS_TOPIC_ARN is NOT set
            # Then: Email not sent and user stays on the same page
            assert TemplateNames.CONTACT_US.value in [
                t.name for t in response.templates
            ]
            assert response.status_code == HTTPStatus.OK.value

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_post_empty_form(self, client):
        """When a user submits an empty form, it will redirect to the current page"""
        # When: POST request on the contact us page, with an empty form
        contact_us_url = reverse("contact_us")
        response = client.post(contact_us_url, data={}, HTTP_REFERER=contact_us_url)
        # Then: the rendered template is the current `contact-us` template
        assert TemplateNames.CONTACT_US.value in [t.name for t in response.templates]
        assert response.status_code == HTTPStatus.OK.value

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
        """Ensures page rediction when invalid form is submitted"""
        # Given: Form with invalid data
        invalid_form = ContactForm()
        invalid_form.name = name
        invalid_form.contact_email = contact_email
        invalid_form.subject = subject
        invalid_form.message = message
        # When: the form is posted on the contact-us page
        contact_us_url = reverse("contact_us")
        response = client.post(
            contact_us_url, data=invalid_form.json(), HTTP_REFERER=contact_us_url,
        )
        # Then: user stays on the contact-us page
        assert TemplateNames.CONTACT_US.value in [t.name for t in response.templates]
        assert response.status_code == HTTPStatus.OK.value
