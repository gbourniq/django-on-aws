from .base import *

"""
Local settings are suitable for a baremetal deployment:
- DEBUG = True
- Local postgres
- No Email backend configuration
- No cache settings (redis)
- No celery settings
- Local storage for django files (media/static)
"""

print(f"Loading Django settings")

DEBUG = True

ENABLE_LOGIN_REQUIRED_MIXIN = False

# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_PORT = 587
# EMAIL_HOST_USER = config.EMAIL_HOST_USER
# EMAIL_HOST_PASSWORD = config.EMAIL_HOST_PASSWORD
# EMAIL_USE_TLS = True
# EMAIL_TIMEOUT = 10

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config.POSTGRES_DB,
        "USER": config.POSTGRES_USER,
        "PASSWORD": config.POSTGRES_PASSWORD,
        "HOST": "localhost",
        "PORT": config.POSTGRES_PORT,
    }
}

# FILE STORAGE
STATIC_URL = "/staticfiles/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_URL = "/" + config.MEDIA_URL + "/"
MEDIA_ROOT = os.path.join(BASE_DIR, config.MEDIA_URL)
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
