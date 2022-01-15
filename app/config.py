"""Main configuration parameters for FastAPI and Lambda powertools"""
import logging
from distutils.util import strtobool
from os import getenv
from pathlib import Path

from starlette.config import Config
from starlette.datastructures import Secret

logger = logging.getLogger(__name__)

# Paths
APP_DIR = Path(__file__).resolve().parent
ENV_PATH = APP_DIR / ".env"
logger.info(f"Loading Django configs environment variables from {ENV_PATH}")

config = Config(env_file=ENV_PATH)

# ======================= SETTINGS.PY =========================

# General settings
DEBUG: bool = bool(strtobool(getenv("DEBUG", "True")))
SECRET_KEY: Secret = getenv("SECRET_KEY", config("SECRET_KEY", cast=Secret))
STATIC_FILES_PATH: str = "staticfiles/"
MEDIA_FILES_PATH: str = "mediafiles/"

# Postgres
POSTGRES_HOST: str = getenv(
    "POSTGRES_HOST", config("POSTGRES_HOST", default="localhost")
)
POSTGRES_PASSWORD: Secret = getenv(
    "POSTGRES_PASSWORD", config("POSTGRES_PASSWORD", cast=Secret, default="postgres")
)
POSTGRES_DB: str = getenv("POSTGRES_DB", config("POSTGRES_DB", default="portfoliodb"))
POSTGRES_PORT: int = getenv(
    "POSTGRES_PORT", config("POSTGRES_PORT", cast=int, default=5432)
)
POSTGRES_USER: str = getenv(
    "POSTGRES_USER", config("POSTGRES_USER", default="postgres")
)

# Redis Cache
# Get from environment variable, for example if ElastiCache is used,
# Otherwise assume Redis running in a docker container named "redis"
REDIS_ENDPOINT: str = getenv(
    "REDIS_ENDPOINT", config("REDIS_ENDPOINT", default="localhost:6379")
)
CACHE_TTL: int = int(getenv("CACHE_TTL", "60"))

# Static files served from AWS S3 Bucket
STATICFILES_BUCKET: str = getenv("STATICFILES_BUCKET")
AWS_REGION: str = getenv("AWS_REGION", "eu-west-2")
AWS_S3_CUSTOM_DOMAIN: str = getenv(
    "AWS_S3_CUSTOM_DOMAIN", f"s3.{AWS_REGION}.amazonaws.com/{STATICFILES_BUCKET}"
)  # E.g. tari.kitchen

# Forward ContactForm emails to AWS SNS Topic
SNS_TOPIC_ARN: str = getenv("SNS_TOPIC_ARN", config("SNS_TOPIC_ARN", default=None))

# SES identity for email notifications
SES_IDENTITY_ARN: str = getenv(
    "SES_IDENTITY_ARN", config("SES_IDENTITY_ARN", default=None)
)
