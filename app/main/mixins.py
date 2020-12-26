import logging
import sys
from collections import namedtuple
from io import BytesIO

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.fields.files import ImageFieldFile
from PIL import Image

DIMS = namedtuple("DIMS", "width height")


class RequireLoginMixin:
    """Add this Mixin in django class views to enforce user to log in"""

    def dispatch(self, request, *args, **kwargs):
        if settings.ENABLE_LOGIN_REQUIRED_MIXIN and not request.user.is_authenticated:
            return redirect_to_login(next=request.get_full_path(), login_url="/login")
        return super(RequireLoginMixin, self).dispatch(request, *args, **kwargs)


class BaseModelMixin:
    """
    Base Class providing helper functions for Django Models
    """

    logger = logging.getLogger(__name__)

    def resizeImage(self, uploadedImage: ImageFieldFile) -> ImageFieldFile:
        """
        Performs the following operation on a given image:
        - Thumbmail: returns an image that fits inside of a given size
        - Crop: Cut image borders to fit a given size
        """
        thumbnail_size = DIMS(500, 500)
        crop_size = DIMS(300, 300)

        img_temp = Image.open(uploadedImage)
        output_io_stream = BytesIO()

        img_temp.thumbnail(thumbnail_size)
        width, height = img_temp.size

        left = (width - crop_size.width) / 2
        top = (height - crop_size.height) / 2
        right = (width + crop_size.width) / 2
        bottom = (height + crop_size.height) / 2

        img_temp = img_temp.crop((left, top, right, bottom))

        img_temp.save(output_io_stream, format="JPEG", quality=90)
        output_io_stream.seek(0)
        uploadedImage = InMemoryUploadedFile(
            output_io_stream,
            "ImageField",
            "%s.jpg" % uploadedImage.name.split(".")[0],
            "image/jpeg",
            sys.getsizeof(output_io_stream),
            None,
        )
        return uploadedImage
