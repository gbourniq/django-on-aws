"""Main configuration parameters for FastAPI and Lambda powertools"""
from os import getenv
from pathlib import Path
from distutils.util import strtobool
from starlette.config import Config
from starlette.datastructures import Secret

# Paths
APP_DIR = Path(__file__).resolve().parent
ENV_PATH = APP_DIR / ".env"
print(f"Loading configs from {ENV_PATH}")
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

# Static files served from AWS S3 Bucket
STATICFILES_BUCKET: str = getenv("STATICFILES_BUCKET")
AWS_REGION: str = getenv("AWS_REGION", "eu-west-2")
