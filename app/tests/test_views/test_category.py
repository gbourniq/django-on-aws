import pytest
from django.db.models.query import QuerySet
from django.urls import reverse


@pytest.mark.django_db(transaction=True)
class TestViewCategory:
    @pytest.mark.integration
    def test_404_no_category_in_db(self, client):
        """
        Test that 404 is handled when no category exist
        """

        response = client.get(reverse("categories_view"))

        assert "main/go_back_home.html" in [t.name for t in response.templates]
        assert response.status_code == 200
        assert response.context["code_handled"] == 404

    @pytest.mark.integration
    def test_view_category(self, client, load_default_category):
        """
        Test the view Category page when database contains one category object
        """

        response = client.get(reverse("categories_view"))

        assert "main/categories.html" in [t.name for t in response.templates]
        assert response.status_code == 200

        assert isinstance(response.context["all_categories_list"], QuerySet)
