FROM python:3.8-slim-buster

# Change default shell to /bin/bash
SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

ARG APP_WHEEL=dist/*.whl
ARG APP_DIR=app
ARG MOUNT_DIR=mounts
ARG STARTUP_SCRIPT=deployment/config/startup_server.sh
ARG USERNAME="portfoliouser"

ENV PATH="/opt/venv/bin:${PATH}" \
    PYTHONPATH="/home/${USERNAME}/${APP_DIR}/" \
    DJANGO_SETTINGS_MODULE="portfolio.settings" \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# hadolint ignore=DL3008
RUN apt-get update && \
    # Add additional basic packages.
    # * gcc libpq-dev python3-dev: psycopg2 source dependencies
    # * curl: to healthcheck services with http response
    # * vim: editing files
    # * procps: useful utilities such as ps, top, vmstat, pgrep,...
    apt-get install -yq --no-install-recommends gcc libpq-dev python3-dev curl vim procps
    # Clean the apt cache
    # rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
# hadolint ignore=DL3020
ADD $APP_WHEEL /tmp
# hadolint ignore=DL3013
RUN python -m venv /opt/venv && \
    # Install python dependencies
    pip install /tmp/*.whl && \
    rm -rf /tmp/*

# Copy application code and startup script
COPY ${APP_DIR}/ /home/${USERNAME}/${APP_DIR}
COPY ${STARTUP_SCRIPT} /home/${USERNAME}/${MOUNT_DIR}/

# Add user
RUN adduser --disabled-password --gecos "" "${USERNAME}" && \
    chown -R "${USERNAME}":"${USERNAME}" /home
USER ${USERNAME}

# Webserver will be running on this port
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=30s --retries=3 CMD curl --fail http://localhost:8080 || exit 1

# hadolint ignore=DL3000
WORKDIR "/home/${USERNAME}/"

CMD ["./mounts/startup_server.sh"]