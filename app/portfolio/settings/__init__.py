"""
This module defines configurations on top on app/portfolio/settings/base.py.
Here we define a basic application with
- No Email backend configuration
- No cache settings (redis)
- No celery settings
- Local storage for django files (media/static)
"""

from .base import *

print("Loading Django settings")

DEBUG = config.DEBUG

ENABLE_LOGIN_REQUIRED_MIXIN = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config.POSTGRES_DB,
        "USER": config.POSTGRES_USER,
        "PASSWORD": config.POSTGRES_PASSWORD,
        "HOST": config.POSTGRES_HOST,
        "PORT": config.POSTGRES_PORT,
    }
}

# FILE STORAGE - s3 static settings & s3 public media settings
if not config.STATICFILES_BUCKET:
    print("Using local filesystem for static files")
    STATIC_URL = config.STATIC_FILES_PATH
    STATIC_ROOT = os.path.join(BASE_DIR, STATIC_URL)
    MEDIA_URL = config.MEDIA_FILES_PATH
    MEDIA_ROOT = os.path.join(BASE_DIR, MEDIA_URL)
    STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
else:
    print(f"Using S3 Bucket {config.STATICFILES_BUCKET} for static files")
    # Extra variables for AWS
    AWS_STORAGE_BUCKET_NAME = config.STATICFILES_BUCKET
    AWS_DEFAULT_REGION = config.AWS_REGION
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    AWS_S3_CUSTOM_DOMAIN = f"s3.{config.AWS_REGION}.amazonaws.com/{AWS_STORAGE_BUCKET_NAME}"
    # Django variables
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{config.STATIC_FILES_PATH}/"
    STATICFILES_STORAGE = "main.storage_backends.StaticStorage"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{config.MEDIA_FILES_PATH}/"
    DEFAULT_FILE_STORAGE = "main.storage_backends.PublicMediaStorage"
    STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
