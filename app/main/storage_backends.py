"""
This module defines configurations for using S3 as a Django storage
backend for static and media files
"""

from storages.backends.s3boto3 import S3Boto3Storage

from app.config import MEDIA_FILES_PATH, STATIC_FILES_PATH


# pylint: disable=abstract-method
class StaticStorage(S3Boto3Storage):
    """Class used in settings.py to specify the S3 folder storing static files"""

    location = STATIC_FILES_PATH
    default_acl = "public-read"


# pylint: disable=abstract-method
class PublicMediaStorage(S3Boto3Storage):
    """Class used in settings.py to specify the S3 folder storing media files"""

    location = MEDIA_FILES_PATH
    default_acl = "public-read"
    file_overwrite = False
