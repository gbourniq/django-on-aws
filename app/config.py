"""Main configuration parameters for FastAPI and Lambda powertools"""
from os import getenv
from pathlib import Path

from starlette.config import Config
from starlette.datastructures import Secret

# Paths
APP_DIR = Path(__file__).resolve().parent
ENV_PATH = APP_DIR / ".env"
print(f"Loading configs from {ENV_PATH}")
config = Config(env_file=ENV_PATH)

# ======================= SETTINGS.PY =========================

# General settings
SECRET_KEY: Secret = getenv("SECRET_KEY", config("SECRET_KEY", cast=Secret))
MEDIA_URL: str = getenv("MEDIA_URL", config("MEDIA_URL", default="mediafiles"))

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


# ==================== AWS ======================
# AWS_STORAGE_BUCKET_NAME: str = config("AWS_STORAGE_BUCKET_NAME")
# AWS_DEFAULT_REGION: str = config("AWS_DEFAULT_REGION")
