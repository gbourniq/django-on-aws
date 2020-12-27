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
SECRET_KEY: Secret = config("SECRET_KEY", cast=Secret)
MEDIA_URL: str = config("MEDIA_URL", default="mediafiles")

# Postgres
POSTGRES_HOST: str = getenv("POSTGRES_HOST", config("POSTGRES_HOST"))
POSTGRES_PORT: int = config("POSTGRES_PORT", cast=int)
POSTGRES_DB: str = config("POSTGRES_DB")
POSTGRES_USER: str = config("POSTGRES_USER")
POSTGRES_PASSWORD: Secret = config("POSTGRES_PASSWORD", cast=Secret)

# ==================== AWS ======================
# AWS_STORAGE_BUCKET_NAME: str = config("AWS_STORAGE_BUCKET_NAME")
# AWS_DEFAULT_REGION: str = config("AWS_DEFAULT_REGION")
