import pytest
from django.urls import reverse

from helpers import strings


class TestInvalidUrl:
    @pytest.mark.integration
    def test_invalid_url(self, client):
        """Tests that invalid url paths are handled"""

        response = client.get(reverse("error404"))

        assert response.status_code == 200
        assert response.context["code_handled"] == 404
        assert response.context["message"] == strings.MSG_404
        assert "main/go_back_home.html" in [t.name for t in response.templates]
