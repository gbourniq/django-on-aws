import shutil
from pathlib import Path
from typing import List, Tuple
from unittest.mock import Mock

import pytest
from django.db.models.fields.files import ImageFieldFile
from PIL import UnidentifiedImageError

from app.static_settings import MEDIA_URL
from app.tests.mocks import MockCategory
from app.tests.utils import (
    check_image_attributes,
    create_dummy_file,
    create_dummy_png_image,
)
from main.mixins import BaseModelMixin
from main.models import Category


@pytest.mark.django_db(transaction=True)
class TestCategory:
    def test_create_category(self, mock_default_category: Category):
        """
        Test category created with the expected attributes
        """

        _id = MockCategory.DEFAULT_ID

        attr_mapping = {
            mock_default_category.category_name: f"{MockCategory.DEFAULT_CATEGORY_NAME}{_id}",
            mock_default_category.summary: f"{MockCategory.DEFAULT_SUMMARY}{_id}",
            mock_default_category.image: f"{MockCategory.DEFAULT_IMAGE_NAME}{_id}.{MockCategory.DEFAULT_IMAGE_EXTENSION}",
            mock_default_category.category_slug: f"{MockCategory.DEFAULT_CATEGORY_SLUG}{_id}",
        }

        assert all(
            cat_attr == dummy_var
            for cat_attr, dummy_var in attr_mapping.items()
        )

    def test_attr_types(self, mock_default_category: Category):
        """
        Test category created with the expected attributes types
        """

        type_mapping = {
            mock_default_category.category_name: str,
            mock_default_category.summary: str,
            mock_default_category.image: ImageFieldFile,
            mock_default_category.category_slug: str,
        }

        assert all(
            isinstance(attr, attr_type)
            for attr, attr_type in type_mapping.items()
        )

    def test_category_str_cast(self, mock_default_category: Category):
        """
        Test category str() method is overridden
        """
        assert str(mock_default_category) == mock_default_category.category_name

    def test_category_repr_cast(self, mock_default_category: Category):
        """
        Tests Category repr() method is overridden
        """
        assert (
            repr(mock_default_category)
            == f"Category=(id={mock_default_category.id},category_name={mock_default_category.category_name},category_slug={mock_default_category.category_slug})"
        )

    def test_category_json_cast(self, mock_default_category: Category):
        """
        Test category .json() method
        """
        expected_dict = {
            "category_name": mock_default_category.category_name,
            "summary": mock_default_category.summary,
            "image": mock_default_category.image,
            "category_slug": mock_default_category.category_slug,
        }
        assert mock_default_category.to_json() == expected_dict

    def test_category_list_class_property(
        self, load_default_categories: List[Category]
    ):
        """
        Tests __category_list contains a list of saved categories
        """
        assert Category.get_category_list() == load_default_categories

    def test_image_resize_called(
        self, monkeypatch, mock_default_category: Category
    ):
        """
        Ensures the resizeImage function is called when saving a category
        """
        mock_resize_image = Mock(return_value=mock_default_category.image)
        monkeypatch.setattr(Category, "resizeImage", mock_resize_image)

        mock_default_category.save()

        mock_resize_image.assert_called_once_with(mock_default_category.image)

    @pytest.mark.parametrize(
        "INITIAL_SIZE", [(800, 1280), (2000, 200), (200, 2000), (100, 100)]
    )
    @pytest.mark.parametrize("FILE_EXTENTION", ["png", "jpeg", "bmp", "tiff"])
    def test_image_resize_success(
        self,
        mock_default_category: Category,
        INITIAL_SIZE: Tuple[int, int],
        FILE_EXTENTION: str,
    ):
        """
        Test that the resizeImage function works as expected
        when saving a Category object
        """

        mock_default_category.image = f"dummy_image_base_name.{FILE_EXTENTION}"
        create_dummy_png_image(
            mock_default_category.image.name, IMAGE_SIZE=INITIAL_SIZE
        )

        check_image_attributes(
            mock_default_category.image,
            size_check=INITIAL_SIZE,
            ext_check=f".{FILE_EXTENTION}",
        )

        mock_default_category.save()

        check_image_attributes(
            mock_default_category.image,
            size_check=BaseModelMixin.CROP_SIZE,
            ext_check=".jpg",
        )

        shutil.rmtree(Path(MEDIA_URL))

    @pytest.mark.parametrize(
        "FILE_EXTENTION, EXCEPTION",
        [
            ("oops", UnidentifiedImageError),
            ("pdf", UnidentifiedImageError),
            ("txt", UnidentifiedImageError),
            ("docx", UnidentifiedImageError),
            ("xls", UnidentifiedImageError),
        ],
    )
    def test_image_resize_failed(
        self,
        mock_default_category: Category,
        FILE_EXTENTION: str,
        EXCEPTION: Exception,
    ):
        """
        Test the expected Exception is raised when an invalid file format is submitted.
        Clean up created test images
        """

        mock_default_category.image = f"dummy_image_base_name.{FILE_EXTENTION}"
        create_dummy_file(mock_default_category.image.name)

        with pytest.raises(EXCEPTION):
            mock_default_category.save()

        shutil.rmtree(Path(MEDIA_URL))

    def test_load_categories(self, load_default_categories: List[Category]):
        """
        Test that load_default_categories insert the expected number
        of Category objects into the database
        """

        assert Category.objects.all().count() == len(load_default_categories)

    def test_send_notification_is_called_on_save(
        self,
        monkeypatch,
        mock_default_category: Category,
        mock_email_host_user: str,
    ):
        """
        Ensures the send_email_notification_to_users function is called when saving a category
        """

        mock_resize_image = Mock(return_value=mock_default_category.image)
        monkeypatch.setattr(Category, "resizeImage", mock_resize_image)

        mock_send_email_notification = Mock()
        monkeypatch.setattr(
            Category,
            "send_email_notification_to_users",
            mock_send_email_notification,
        )

        mock_default_category.save()

        mock_send_email_notification.assert_called_once()
