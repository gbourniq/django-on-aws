"""
This module defines common functionalities across Django models and Views
"""

import logging
import sys
from io import BytesIO

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.fields.files import ImageFieldFile
from PIL import Image

from helpers.constants import CROP_SIZE, THUMBNAIL_SIZE


class RequireLoginMixin:
    """Add this Mixin in django class views to enforce logging in"""

    def dispatch(self, request, *args, **kwargs):
        """
        Overrides the dispatch method, to check if user is logged in
        before returning the HTTP response.
        """
        if settings.ENABLE_LOGIN_REQUIRED_MIXIN and not request.user.is_authenticated:
            return redirect_to_login(next=request.get_full_path(), login_url="/login")
        return super().dispatch(request, *args, **kwargs)


class BaseModelMixin:
    """Base Class providing helper functions for Django Models"""

    logger = logging.getLogger(__name__)

    # pylint: disable=no-self-use
    def resize_image(
        self, uploaded_image: ImageFieldFile, suffix: str = None
    ) -> ImageFieldFile:
        """
        Performs the following operation on a given image:
        - Thumbmail: returns an image that fits inside of a given size
        - Crop: Cut image borders to fit a given size
        """

        img_temp = Image.open(uploaded_image)

        img_temp.thumbnail(THUMBNAIL_SIZE)
        width, height = img_temp.size

        left = (width - CROP_SIZE.width) / 2
        top = (height - CROP_SIZE.height) / 2
        right = (width + CROP_SIZE.width) / 2
        bottom = (height + CROP_SIZE.height) / 2

        img_temp = img_temp.crop((left, top, right, bottom))
        img_temp = img_temp.convert("RGB")
        img_temp.save(output_io_stream := BytesIO(), format="JPEG", quality=90)
        output_io_stream.seek(0)
        new_filename = f"{uploaded_image.name.split('.')[0]}{suffix}.jpg"
        uploaded_image = InMemoryUploadedFile(
            output_io_stream,
            "ImageField",
            new_filename,
            "image/jpeg",
            sys.getsizeof(output_io_stream),
            None,
        )
        return uploaded_image
