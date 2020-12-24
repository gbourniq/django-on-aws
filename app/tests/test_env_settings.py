from typing import Dict

from django.conf import settings


class TestDjangoDevSettings:
    """
    Class to test that settings.py is configured correctly for dev environments
    - ensures Celery/Redis not configured
    - ensures S3 variables not configured
    """

    def test_cache_settings(self):
        """
        Test the cache settings are not loaded
        """

        assert settings.CACHES != {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": "redis://redis:6379/1",
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient"
                },
                "KEY_PREFIX": "example",
            }
        }

    def test_celery_settings(self):
        """
        Test the celery settings are not loaded
        """

        assert all(
            not hasattr(settings, attr)
            for attr in [
                "CELERY_RESULT_BACKEND",
                "CELERY_REDIS_MAX_CONNECTIONS",
                "CELERY_ALWAYS_EAGER",
                "CELERY_ACKS_LATE",
                "CELERY_TASK_PUBLISH_RETRY",
                "CELERY_DISABLE_RATE_LIMITS",
                "CELERY_SEND_TASK_ERROR_EMAILS",
                "CELERY_TASK_RESULT_EXPIRES",
                "CELERY_DEFAULT_QUEUE",
            ]
        )

    def test_aws_settings(self):
        """
        Test the AWS settings are not loaded
        """

        assert all(
            not hasattr(settings, attr)
            for attr in [
                "AWS_STORAGE_BUCKET_NAME",
                "AWS_DEFAULT_REGION",
                "AWS_DEFAULT_ACL",
                "AWS_S3_OBJECT_PARAMETERS",
                "AWS_S3_CUSTOM_DOMAIN",
            ]
        )

    def test_logging_settings(self):
        """
        Test the LOGGING settings are loaded
        """

        assert all(hasattr(settings, attr) for attr in ["LOGGING",])
        assert isinstance(settings.LOGGING, Dict)
