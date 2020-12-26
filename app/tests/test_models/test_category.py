"""This module defines tests for the Category django model"""

from typing import List, Tuple
from unittest.mock import Mock

import pytest
from django.db.models.fields.files import ImageFieldFile
from PIL import UnidentifiedImageError

from helpers.constants import CROP_SIZE, IMG_EXT
from main.models import Category
from tests.mocks import MockCategory
from tests.utils import (
    check_image_attributes,
    cleanup_media_dir,
    create_dummy_file,
    create_dummy_png_image,
)


@pytest.mark.django_db(transaction=True)
class TestCategory:
    """Tests for the Item django model"""

    # pylint: disable=no-self-use
    def test_create_category(self, mock_default_category: Category):
        """Test category created with the expected attributes"""

        _id = MockCategory.DEFAULT_ID

        attr_mapping = {
            mock_default_category.category_name: f"{MockCategory.DEFAULT_CATEGORY_NAME}{_id}",  # pylint: disable=line-too-long
            mock_default_category.summary: f"{MockCategory.DEFAULT_SUMMARY}{_id}",
            mock_default_category.image: f"{MockCategory.DEFAULT_IMG_NAME}{_id}.{MockCategory.DEFAULT_IMG_EXT}",  # pylint: disable=line-too-long
            mock_default_category.category_slug: f"{MockCategory.DEFAULT_CATEGORY_SLUG}{_id}",  # pylint: disable=line-too-long
        }

        assert all(
            cat_attr == dummy_var for cat_attr, dummy_var in attr_mapping.items()
        )

    # pylint: disable=no-self-use
    def test_attr_types(self, mock_default_category: Category):
        """Test category created with the expected attributes types"""

        type_mapping = {
            mock_default_category.category_name: str,
            mock_default_category.summary: str,
            mock_default_category.image: ImageFieldFile,
            mock_default_category.category_slug: str,
        }

        assert all(
            isinstance(attr, attr_type) for attr, attr_type in type_mapping.items()
        )

    # pylint: disable=no-self-use
    def test_category_str_cast(self, mock_default_category: Category):
        """Test category str() method is overridden"""
        assert str(mock_default_category) == mock_default_category.category_name

    # pylint: disable=no-self-use
    def test_category_repr_cast(self, mock_default_category: Category):
        """
        Tests Category repr() method is overridden
        """
        assert repr(mock_default_category) == (
            f"Category=(id={mock_default_category.id},category_name="
            f"{mock_default_category.category_name},category_slug="
            f"{mock_default_category.category_slug})"
        )

    # pylint: disable=no-self-use
    def test_image_resize_called(self, monkeypatch, mock_default_category: Category):
        """Ensures the resize_image function is called when saving a category"""
        mock_resize_image = Mock(return_value=mock_default_category.image)
        monkeypatch.setattr(Category, "resize_image", mock_resize_image)

        mock_default_category.save()

        mock_resize_image.assert_called_once_with(mock_default_category.image)

    @pytest.mark.parametrize(
        "initial_size", [(800, 1280), (2000, 200), (200, 2000), (100, 100)]
    )
    @pytest.mark.parametrize("file_extension", ["png", "jpeg", "bmp", "tiff"])
    # pylint: disable=no-self-use
    def test_image_resize_success(
        self,
        mock_default_category: Category,
        initial_size: Tuple[int, int],
        file_extension: str,
    ):
        """
        Test that the resize_image function works as expected
        when saving a Category object
        """

        mock_default_category.image = f"dummy_image_base_name.{file_extension}"
        create_dummy_png_image(
            mock_default_category.image.name, image_size=initial_size
        )

        check_image_attributes(
            mock_default_category.image,
            size_check=initial_size,
            ext_check=f".{file_extension}",
        )

        mock_default_category.save()

        check_image_attributes(
            mock_default_category.image, size_check=CROP_SIZE, ext_check=IMG_EXT,
        )

        cleanup_media_dir()

    @pytest.mark.parametrize(
        "file_extension, exception",
        [
            ("oops", UnidentifiedImageError),
            ("pdf", UnidentifiedImageError),
            ("txt", UnidentifiedImageError),
            ("docx", UnidentifiedImageError),
            ("xls", UnidentifiedImageError),
        ],
    )
    # pylint: disable=no-self-use
    def test_image_resize_failed(
        self,
        mock_default_category: Category,
        file_extension: str,
        exception: Exception,
    ):
        """
        Test the expected Exception is raised when an invalid file format is submitted.
        Clean up created test images
        """

        mock_default_category.image = f"dummy_image_base_name.{file_extension}"
        create_dummy_file(mock_default_category.image.name)

        with pytest.raises(exception):
            mock_default_category.save()

        cleanup_media_dir()

    # pylint: disable=no-self-use
    def test_load_categories(self, load_default_categories: List[Category]):
        """
        Test that load_default_categories insert the expected number
        of Category objects into the database
        """

        assert Category.objects.all().count() == len(load_default_categories)
