import logging
import sys
from collections import namedtuple
from io import BytesIO
from typing import List, Union

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.views import redirect_to_login
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.mail import BadHeaderError, send_mail
from django.db.models.fields.files import ImageFieldFile
from PIL import Image


class RequireLoginMixin:
    """
    Add this Mixin in django class views to enforce logging
    """

    def dispatch(self, request, *args, **kwargs):
        if (
            settings.ENABLE_LOGIN_REQUIRED_MIXIN
            and not request.user.is_authenticated
        ):
            return redirect_to_login(
                next=request.get_full_path(), login_url="/login"
            )
        return super(RequireLoginMixin, self).dispatch(request, *args, **kwargs)


class JSONifyMixin:
    """
    Abstract class to enforce the implementation
    of the to_json() method
    """

    def to_json(self):
        raise NotImplementedError


class BaseModelMixin:
    """
    Base Class providing helper functions to Django Models
    """

    Dimensions = namedtuple("Dimensions", "width height")
    THUMBNAIL_SIZE = Dimensions(500, 500)
    CROP_SIZE = Dimensions(300, 300)

    logger = logging.getLogger(__name__)

    def resizeImage(self, uploadedImage: ImageFieldFile) -> ImageFieldFile:
        """
        Performs the following operation on a given image:
        - Thumbmail: returns an image that fits inside of a given size
        - Crop: Cut image borders to fit a given size
        """
        img_temp = Image.open(uploadedImage)
        outputIoStream = BytesIO()

        img_temp.thumbnail(self.THUMBNAIL_SIZE)
        width, height = img_temp.size
        left = (width - self.CROP_SIZE.width) / 2
        top = (height - self.CROP_SIZE.height) / 2
        right = (width + self.CROP_SIZE.width) / 2
        bottom = (height + self.CROP_SIZE.height) / 2
        img_temp = img_temp.crop((left, top, right, bottom))

        img_temp.save(outputIoStream, format="JPEG", quality=90)
        outputIoStream.seek(0)
        uploadedImage = InMemoryUploadedFile(
            outputIoStream,
            "ImageField",
            "%s.jpg" % uploadedImage.name.split(".")[0],
            "image/jpeg",
            sys.getsizeof(outputIoStream),
            None,
        )
        return uploadedImage

    def get_registered_emails(self) -> Union[List[str], None]:
        """
        Retrives email addresses of registered users.
        """
        registered_email_addresses = [
            user.email for user in User.objects.all() if user.email
        ]
        if registered_email_addresses is not None:
            return registered_email_addresses
        return None

    def send_email_notification_to_users(
        self,
        subject: str,
        message: str,
        from_email: str = settings.EMAIL_HOST_USER,
    ) -> None:
        """
        Send an email notification to registered users.
        """

        registered_emails = self.get_registered_emails()

        if not registered_emails:
            self.logger.warning(f"No registered emails found")
            return None

        try:
            [
                send_mail(subject, message, from_email, [to_email])
                for to_email in registered_emails
            ]
            self.logger.info(
                f"Email notification sent successfully to {registered_emails}"
            )
        except BadHeaderError:
            self.logger.warning(
                f"Email function {send_mail} returned BadHeaderError"
            )
