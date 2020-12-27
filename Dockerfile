FROM python:3.8-slim-buster

# Change default shell to /bin/bash
SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

ARG APP_WHEEL=dist/*.whl
ARG APP_DIR=app
ARG STARTUP_SCRIPT=deployment/app/startup_server.sh
ARG USERNAME="portfoliouser"

ENV PATH="/opt/venv/bin:${PATH}" \
    PYTHONPATH="/home/${USERNAME}/${APP_DIR}/" \
    DJANGO_SETTINGS_MODULE="portfolio.settings" \
    POSTGRES_HOST="postgres" \
    POSTGRES_PASSWORD="postgres"
    
# Copy application code, startup script, and dependencies
COPY ${APP_DIR}/ ${STARTUP_SCRIPT} /home/${USERNAME}/${APP_DIR}/
# hadolint ignore=DL3020
ADD $APP_WHEEL /tmp

# hadolint ignore=DL3008
RUN apt-get update && \
    # Add additional basic packages.
    # * gcc libpq-dev python3-dev: psycopg2 source dependencies
    # * curl: to healthcheck services with http response
    # * vim: editing files
    # * procps: useful utilities such as ps, top, vmstat, pgrep,...
    apt-get install -yq --no-install-recommends gcc libpq-dev python3-dev curl vim procps && \
    # Clean the apt cache
    rm -rf /var/lib/apt/lists/*

# hadolint ignore=DL3013
RUN python -m venv /opt/venv && \
    # Install python dependencies
    pip install /tmp/*.whl && \
    rm -rf /tmp/* && \
    # Add user
    adduser --disabled-password --gecos "" "${USERNAME}" && \
    chown -R "${USERNAME}":"${USERNAME}" /home

USER ${USERNAME}

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=30s --retries=3 CMD curl --fail http://localhost:8080 || exit 1

# hadolint ignore=DL3000
WORKDIR "/home/${USERNAME}/${APP_DIR}/"

CMD ["./startup_server.sh"]