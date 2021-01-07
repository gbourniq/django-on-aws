# Set shell
SHELL=/bin/bash -e -o pipefail

### Environment variables ###
CONDA_ENV_NAME=django-on-aws
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate

# Docker
DOCKER_USER=gbournique
IMAGE_REPOSITORY=${DOCKER_USER}/django-on-aws
TAG=$(shell poetry version | awk '{print $$NF}')

# Cloudformation
CFN_TEMPLATE_FILE=deployment/cfn-template-app.yaml

### Environment and pre-commit hooks ###
.PHONY: env env-update pre-commit
env:
	@ ${INFO} "Creating ${CONDA_ENV_NAME} conda environment and poetry dependencies"
	@ conda env create -f environment.yml -n $(CONDA_ENV_NAME)
	@ ($(CONDA_ACTIVATE) $(CONDA_ENV_NAME); poetry install)
	@ ${SUCCESS} "${CONDA_ENV_NAME} conda environment has been created and dependencies installed with Poetry."
	@ ${MESSAGE} "Please activate the environment with: conda activate ${CONDA_ENV_NAME}"

env-update:
	@ ${INFO} "Updating ${CONDA_ENV_NAME} conda environment and poetry dependencies"
	@ conda env update -f environment.yml -n $(CONDA_ENV_NAME)
	@ ($(CONDA_ACTIVATE) $(CONDA_ENV_NAME); poetry update)
	@ ${SUCCESS} "${CONDA_ENV_NAME} conda environment and poetry dependencies have been updated!"
 
pre-commit:
	@ pre-commit install -t pre-commit -t commit-msg
	@ ${SUCCESS} "pre-commit set up"


### Development and Testing ###
.PHONY: runserver tests open-cov-report

rundb:
	@ docker-compose up -d postgres || true

recreatedb: rundb
	@ ${INFO} "Wiping portfoliodb table"
	docker exec -it --user=postgres postgres dropdb portfoliodb
	docker exec -it --user=postgres postgres createdb portfoliodb

runserver: rundb
	@ python app/manage.py migrate --run-syncdb
	@ python app/manage.py runserver 0.0.0.0:8080

tests: rundb
	@ ${INFO} "Running Django tests with PostgreSQL running on Docker"
	@ pytest app -x
	@ docker-compose down || true
	@ ${INFO} "Run 'make open-cov-report' to view coverage details"

open-cov-report:
	@ open htmlcov/index.html


### Deployment ###
.PHONY: image up down publish
image:
	rm -rf dist
	poetry build
	docker build -t ${IMAGE_REPOSITORY}:$(TAG) .

up:
	@ ${INFO} "Running Django tests with PostgreSQL running on Docker"
	@ docker-compose down
	@ docker-compose up -d

healthcheck:
	@ ${INFO} "Checking Django application health"
	@ ./utils/healthcheck.sh

down:
	@ docker-compose down

publish:
	@ echo "${DOCKER_PASSWORD}" | docker login --username "${DOCKER_USER}" --password-stdin 2>&1
	@ docker push ${IMAGE_REPOSITORY}:$(TAG)

run-app:
	@ ${INFO} "Running Django app as a standalone container"
	@ ${INFO} "Postgres host: ${POSTGRES_HOST} (default: localhost)"
	@ docker run -d \
				-p 8080:8080 \
				--name=myapp \
				--restart=no \
				--env POSTGRES_HOST=${POSTGRES_HOST} \
				--env POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
				${IMAGE_REPOSITORY}:$(TAG)

rm-app:
	@ ${INFO} "Removing Django app container"
	@ docker rm --force $$(docker ps --filter "ancestor=${IMAGE_REPOSITORY}:$(TAG)" -qa)

### CloudFormation ###
cfn-validate:
	@ echo "Validating CloudFormation template ${CFN_TEMPLATE_FILE}"
	@ yamllint -d "{rules: {line-length: {max: 130, level: warning}}}" "${CFN_TEMPLATE_FILE}"
	@ cfn-lint "${CFN_TEMPLATE_FILE}"
	@ aws cloudformation validate-template --template-body file://"${CFN_TEMPLATE_FILE}" > /dev/null 2>&1

cfn-create: cfn-validate
	@ bash ./deployment/create-stack.sh

cfn-update: cfn-validate
	@ bash ./deployment/update-stack.sh

cfn-delete:
	@ bash ./deployment/delete-stack.sh

### Helpers ###
RED := "\e[1;31m"
YELLOW := "\e[1;33m"
GREEN := "\033[32m"
NC := "\e[0m"
INFO := @bash -c 'printf ${YELLOW}; echo "[INFO] $$1"; printf ${NC}' MESSAGE
MESSAGE := @bash -c 'printf ${NC}; echo "$$1"; printf ${NC}' MESSAGE
SUCCESS := @bash -c 'printf ${GREEN}; echo "[SUCCESS] $$1"; printf ${NC}' MESSAGE
WARNING := @bash -c 'printf ${RED}; echo "[WARNING] $$1"; printf ${NC}' MESSAGEs