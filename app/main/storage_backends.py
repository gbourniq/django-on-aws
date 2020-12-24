from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """Class used in settings.py to specify the S3 folder storing static files"""

    location = "django_files/static"
    default_acl = "public-read"


class PublicMediaStorage(S3Boto3Storage):
    """Class used in settings.py to specify the S3 folder storing media files"""

    location = "django_files/media"
    default_acl = "public-read"
    file_overwrite = False
