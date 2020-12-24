import pytest
from django.urls import reverse


@pytest.mark.django_db(transaction=True)
class TestViewHome:
    @pytest.mark.integration
    def test_view_homepage(self, client):
        """
        Test the view Homepage is rendered
        """

        response = client.get(reverse("home"))

        assert "main/home.html" in (t.name for t in response.templates)
        assert response.status_code == 200
