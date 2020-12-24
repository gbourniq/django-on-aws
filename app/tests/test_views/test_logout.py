from unittest.mock import Mock

import pytest
from django.urls import reverse


@pytest.mark.django_db(transaction=True)
class TestViewLogout:
    @pytest.mark.integration
    def test_click_logout_button(self, monkeypatch, client):
        """
        Tests that logout function is called,
        and redirection to home
        """

        mock_logout = Mock()
        monkeypatch.setattr("main.views.logout", mock_logout)

        response = client.get(reverse("logout"))

        assert len(response.templates) == 0
        assert response.status_code == 302
        mock_logout.assert_called_with(response.wsgi_request)
