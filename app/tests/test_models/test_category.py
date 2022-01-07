"""This module defines tests for the Category django model"""

from typing import List, Tuple
from unittest.mock import Mock

import pytest
from django.conf import settings
from django.db.models.fields.files import ImageFieldFile
from PIL import UnidentifiedImageError

from helpers.constants import CROP_SIZE, IMG_EXT
from main.models import Category
from tests.mocks import MockCategory
from tests.utils import (
    check_image_attributes,
    create_dummy_file,
    create_dummy_png_image,
)


@pytest.mark.django_db(transaction=True)
class TestCategory:
    """Tests for the Item django model"""

    # pylint: disable=no-self-use
    def test_create_mock_category(self, mock_default_category: Category):
        """Test category created with the expected attributes"""
        # Given: Default field values defined in mock.py
        # When: the mock_default_category fixture is called
        _id = MockCategory.DEFAULT_ID
        attr_mapping = {
            mock_default_category.category_name: f"{MockCategory.DEFAULT_CATEGORY_NAME}{_id}",  # pylint: disable=line-too-long
            mock_default_category.summary: f"{MockCategory.DEFAULT_SUMMARY}{_id}",
            mock_default_category.image: f"{MockCategory.DEFAULT_IMG_NAME}{_id}.{MockCategory.DEFAULT_IMG_EXT}",  # pylint: disable=line-too-long
        }

        # Then: Category object fields have been assigned correctly
        assert all(
            cat_attr == dummy_var for cat_attr, dummy_var in attr_mapping.items()
        )

    # pylint: disable=no-self-use
    def test_attr_types(self, mock_default_category: Category):
        """Test category created with the expected attributes types"""
        # Given: Default field values defined in mock.py
        # When: the mock_default_category fixture is called
        type_mapping = {
            mock_default_category.category_name: str,
            mock_default_category.summary: str,
            mock_default_category.image: ImageFieldFile,
            mock_default_category.category_slug: str,
        }
        # Then: Category object fields have the correct types
        assert all(
            isinstance(attr, attr_type) for attr, attr_type in type_mapping.items()
        )

    # pylint: disable=no-self-use
    def test_category_str_cast(self, mock_default_category: Category):
        """Test category str() method is overridden"""
        assert str(mock_default_category) == mock_default_category.category_name

    # pylint: disable=no-self-use
    def test_category_repr_cast(self, mock_default_category: Category):
        """Tests Category repr() method is overridden"""
        assert repr(mock_default_category) == (
            f"Category=(id={mock_default_category.id},category_name="
            f"{mock_default_category.category_name},category_slug="
            f"{mock_default_category.category_slug})"
        )

    # pylint: disable=no-self-use
    def test_load_categories(self, load_default_categories: List[Category]):
        """Test that load_default_categories does insert Category objects in the DB"""
        assert Category.objects.all().count() == len(load_default_categories)

    # pylint: disable=no-self-use
    def test_mock_categories(self, mock_default_categories: List[Category]):
        """
        Test that mock_default_categories fixture does return Category objects
        but will not save them into the DB
        """
        assert Category.objects.all().count() == 0
        assert all(isinstance(obj, Category) for obj in mock_default_categories)

    # pylint: disable=no-self-use
    def test_image_resize_called(self, monkeypatch, mock_default_category: Category):
        """Ensures the resize_image function is called when saving a category"""
        # Given: a mock resize_image function
        monkeypatch.setattr(
            Category,
            "resize_image",
            mock_resize_image := Mock(return_value=mock_default_category.image),
        )

        # When: the save method of a Category object is called
        mock_default_category.save()

        # Then: The resize_image function is called
        mock_resize_image.assert_called_once_with(mock_default_category.image)

    @pytest.mark.parametrize(
        "initial_size", [(800, 1280), (2000, 200), (200, 2000), (100, 100)]
    )
    @pytest.mark.parametrize("file_ext", ["png", "jpeg", "bmp", "tiff"])
    # pylint: disable=no-self-use
    # pylint: disable=too-many-arguments
    def test_image_resize_success(
        self,
        monkeypatch,
        tmp_path,
        mock_default_category: Category,
        initial_size: Tuple[int, int],
        file_ext: str,
    ):
        """Ensure resize_image function does its job"""

        # Set Django to store media files to the tmp_path directory
        monkeypatch.setattr(settings, "MEDIA_ROOT", tmp_path)

        # Given: a category with a mock image
        mock_default_category.image = tmp_path / f"dummy_image_base_name.{file_ext}"
        create_dummy_png_image(
            tmp_path, mock_default_category.image.name, image_size=initial_size
        )

        # Then: Image has its initial size before resizing
        check_image_attributes(
            mock_default_category.image, size=initial_size, ext=f".{file_ext}",
        )

        # When: the save method calls resize_image
        mock_default_category.save()

        # Then: Image has its expected size after resizing
        check_image_attributes(
            mock_default_category.image, size=CROP_SIZE, ext=IMG_EXT,
        )

    @pytest.mark.parametrize(
        "file_ext, exception",
        [
            ("oops", UnidentifiedImageError),
            ("pdf", UnidentifiedImageError),
            ("txt", UnidentifiedImageError),
            ("docx", UnidentifiedImageError),
            ("xls", UnidentifiedImageError),
        ],
    )
    # pylint: disable=too-many-arguments
    # pylint: disable=no-self-use
    def test_image_resize_failed(
        self,
        monkeypatch,
        tmp_path,
        mock_default_category: Category,
        file_ext: str,
        exception: Exception,
    ):
        """Expected Exception is raised when providing an invalid file format"""

        # Set Django to store media files to the tmp_path directory
        monkeypatch.setattr(settings, "MEDIA_ROOT", tmp_path)

        # Given: a category with a mock invalid file as an image attribute
        mock_default_category.image = tmp_path / f"invalid_image.{file_ext}"
        create_dummy_file(tmp_path, filename=mock_default_category.image.name)

        # When: The expected is raised when the resize_image function is called
        with pytest.raises(exception):
            mock_default_category.save()
