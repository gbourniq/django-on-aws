"""Main configuration parameters for FastAPI and Lambda powertools"""
from pathlib import Path

from starlette.config import Config
from starlette.datastructures import URL, Secret

# Paths
APP_DIR = Path(__file__).resolve().parent
ENV_PATH = APP_DIR / ".env"
print(f"Loading configs from {ENV_PATH}")
config = Config(env_file=ENV_PATH)

"""
This file collects environment variables across the repo and store them into global
variables. This allows to easily update the code base if in the future a variable
is renamed or removed.
"""

# ======================= SETTINGS.PY =========================

# General settings
SECRET_KEY: Secret = config("SECRET_KEY", cast=Secret)
MEDIA_URL: str = config("MEDIA_URL", default="mediafiles")

# Postgres
POSTGRES_HOST: URL = config("POSTGRES_HOST", cast=URL)
POSTGRES_PORT: int = config("POSTGRES_PORT", cast=int)
POSTGRES_DB: str = config("POSTGRES_DB")
POSTGRES_USER: str = config("POSTGRES_USER")
POSTGRES_PASSWORD: Secret = config("POSTGRES_PASSWORD", cast=Secret)

# Optional - Message Broker for Celery workers
# REDIS_HOST = os.getenv("REDIS_HOST")
# REDIS_PORT = os.getenv("REDIS_PORT", 6379)

# Email details for contact us page
# EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

# ==================== AWS ======================
# AWS_STORAGE_BUCKET_NAME: str = config("AWS_STORAGE_BUCKET_NAME")
# AWS_DEFAULT_REGION: str = config("AWS_DEFAULT_REGION")
