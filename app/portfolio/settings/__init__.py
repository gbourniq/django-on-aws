"""
This module defines additional Django configurations and can be used
to override settings from setting/base.py.
"""

from .base import *


DEBUG = config.DEBUG
print(f"Loading Django settings (DEBUG={DEBUG})")

ENABLE_LOGIN_REQUIRED_MIXIN = False

# Forward ContactForm emails to AWS SNS Topic
SNS_TOPIC_ARN = config.SNS_TOPIC_ARN

# DATABASE
print(f"DB backend config: Host={config.POSTGRES_HOST}")
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

# CACHE
# https://testdriven.io/blog/django-caching/
CACHE_TTL = config.CACHE_TTL
print(f"Redis Cache config: Endpoint={config.REDIS_ENDPOINT}, TTL={CACHE_TTL}s")
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{config.REDIS_ENDPOINT}",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

# FILE STORAGE - s3 static settings & s3 public media settings
if not config.STATICFILES_BUCKET:
    print("Using local filesystem to serve static files")
    STATIC_URL = config.STATIC_FILES_PATH
    STATIC_ROOT = os.path.join(BASE_DIR, STATIC_URL)
    MEDIA_URL = config.MEDIA_FILES_PATH
    MEDIA_ROOT = os.path.join(BASE_DIR, MEDIA_URL)
    STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
else:
    print(f"Using S3 Bucket {config.STATICFILES_BUCKET} to serve static files")
    # Extra variables for AWS
    AWS_STORAGE_BUCKET_NAME = config.STATICFILES_BUCKET
    AWS_S3_CUSTOM_DOMAIN = config.AWS_S3_CUSTOM_DOMAIN
    AWS_DEFAULT_REGION = config.AWS_REGION
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    # Django variables
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{config.STATIC_FILES_PATH}/"
    STATICFILES_STORAGE = "main.storage_backends.StaticStorage"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{config.MEDIA_FILES_PATH}/"
    DEFAULT_FILE_STORAGE = "main.storage_backends.PublicMediaStorage"
    STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
