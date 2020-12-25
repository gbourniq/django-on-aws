FROM python:3.8-slim-buster

# Change default shell to /bin/bash
SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

ARG APP_WHEEL=dist/*.whl
ARG APP_DIR=app
ARG USERNAME="portfoliouser"
ENV PATH="/opt/venv/bin:${PATH}"

# Copy application code and dependencies
# hadolint ignore=DL3020
ADD $APP_WHEEL /tmp
COPY ${APP_DIR}/ /home/"${USERNAME}"

RUN apt-get update && \
    # Add additional basic packages.
    # * gcc libpq-dev python3-dev: psycopg2 source dependencies
    # * curl: to healthcheck services with http response
    # * vim: editing files
    # * procps: useful utilities such as ps, top, vmstat, pgrep,...
    apt-get install -yq --no-install-recommends gcc libpq-dev python3-dev curl vim procps
    # Clean the apt cache
    # rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv && \
    # Install python dependencies
    pip install /tmp/*.whl && \
    rm -rf /tmp/* && \
    # Add user
    adduser --disabled-password --gecos "" "${USERNAME}" && \
    chown -R "${USERNAME}":"${USERNAME}" /home

USER ${USERNAME}

EXPOSE 8080

# hadolint ignore=DL3000
WORKDIR "/home/${USERNAME}"

