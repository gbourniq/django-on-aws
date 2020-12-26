"""This module defines tests for when invalid url paths are hit"""

import pytest
from django.urls import reverse

from helpers import strings


class TestInvalidUrl:
    """Tests for unmatched url paths"""

    @pytest.mark.integration
    # pylint: disable=no-self-use
    def test_invalid_url(self, client):
        """Tests that invalid url paths are handled"""

        response = client.get(reverse("error404"))

        assert response.status_code == 200
        assert response.context["code_handled"] == 404
        assert response.context["message"] == strings.MSG_404
        assert "main/go_back_home.html" in [t.name for t in response.templates]
