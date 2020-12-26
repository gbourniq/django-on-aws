from .base import *

"""
Lightweight configuration:
- No Email backend configuration
- No cache settings (redis)
- No celery settings
- Local storage for django files (media/static)
"""

print("Loading Django settings")

DEBUG = True

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

# FILE STORAGE
STATIC_URL = "/staticfiles/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_URL = "/" + config.MEDIA_URL + "/"
MEDIA_ROOT = os.path.join(BASE_DIR, config.MEDIA_URL)
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
