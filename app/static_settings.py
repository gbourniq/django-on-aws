import os

"""
This file collects environment variables across the repo and store them into global
variables. This allows to easily update the code base if in the future a variable
is renamed or removed.
"""

# ======================= SETTINGS.PY =========================

# General settings
BUILD = os.getenv("BUILD")
SECRET_KEY = os.getenv("SECRET_KEY")
MEDIA_URL = os.getenv("MEDIA_URL", "mediafiles")

# Postgres
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
POSTGRES_DB = os.getenv("POSTGRES_DB", "portfoliodb")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

# Optional - Message Broker for Celery workers
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

# Email details for contact us page
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

# Save logs to log.info
LOGGING_ENABLED = os.getenv("LOGGING_ENABLED") == "True"

# ==================== AWS ======================
# Removed AWS_SECRET_KEY, and AWS_ACCESS_KEY on 31.08.2020
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")

# ======================= CHECK ENV VARIABLES ARE SET =========================

ENV_VARS = [
    "BUILD",
    "SECRET_KEY",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
]

if BUILD == "prod":
    ENV_VARS += [
        "AWS_STORAGE_BUCKET_NAME",
    ]


for ENV_VAR in ENV_VARS:
    if not locals().get(ENV_VAR):
        raise EnvironmentError(
            f"The {ENV_VAR} environment variable has not been "
            "set. Please set this environment variable."
        )
