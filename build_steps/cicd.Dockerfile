ARG CONDA_VERSION=4.9.2
FROM continuumio/miniconda3:${CONDA_VERSION}

ARG POETRY_HOME="/opt/poetry"
ARG WORKDIR=/root/cicd
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    # install poetry to this location
    POETRY_HOME=${POETRY_HOME} \
    # prevent poetry from creating a virtual environment in the project's root
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    # prepend poetry and venv to path
    PATH="${POETRY_HOME}/bin:$PATH" \
    # for docker inspect manifest
    DOCKER_CLI_EXPERIMENTAL=enabled \
    PYTHONPATH=${WORKDIR}

RUN apt-get --allow-releaseinfo-change update \
    && apt-get update \
    && apt-get install --no-install-recommends -yq \
    # jq: for parsing json responses
    # vim: for any troubleshooting
    # curl, wget and unzip: to install software and packages
    # build-essential: for building python deps
    # docker.io: for running docker commands
    # gcc libpq-dev python3-dev: psycopg2 source dependencies
    jq curl vim wget unzip build-essential docker.io gcc libpq-dev python3-dev

ARG DOCKER_COMPOSE_VERSION=1.27.4
ARG POETRY_VERSION=1.0.10
ARG TERRAFORM_VERSION=0.15.1
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py -o ~/get-poetry.py \
    # Install and configure poetry
    && python ~/get-poetry.py --version ${POETRY_VERSION} -y \
    && rm ~/get-poetry.py \
    # Install docker-compose
    && curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose \
    # Install terraform cli
    && wget --quiet https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    && unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    && mv terraform /usr/bin \
    && rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    # Install terraform-docs
    && curl -sSLo ./terraform-docs.tar.gz https://terraform-docs.io/dl/v0.13.0/terraform-docs-v0.13.0-$(uname)-amd64.tar.gz \
    && tar -xzf terraform-docs.tar.gz \
    && chmod +x terraform-docs \
    && mv terraform-docs /usr/bin/terraform-docs \
    && rm terraform-docs.tar.gz \
    # Install tflint
    && wget https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh \
    && sed -i 's/sudo //' install_linux.sh \
    && bash install_linux.sh \
    && rm install_linux.sh \
    # Initialise conda shell
    && echo "source /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc \
    # Upgrade pip
    && pip install --upgrade pip

WORKDIR ${WORKDIR}

COPY environment.yml poetry.lock pyproject.toml ./

# Install poetry dependencies within conda environment
RUN conda env create -f environment.yml -n django-on-aws
SHELL ["conda", "run", "-n", "django-on-aws", "/bin/bash", "-c"]
RUN poetry install

# Activate conda environment for any runtime commands
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "django-on-aws"]

CMD ["tail", "-f", "/dev/null"]