# Oneshell means I can run multiple lines in a recipe in the same shell, so I don't have to
# chain commands together with semicolon
.ONESHELL:

# Set shell
SHELL=/bin/bash

# Conda environment
CONDA_ENV_NAME=django-on-aws
CONDA_CREATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda env create
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate

<<<<<<< HEAD
=======
# Cloudformation
ENVIRONMENT?=live
STACK_NAME=$(ENVIRONMENT)
S3_BUCKET_NAME_CFN_TEMPLATES=gbournique-sam-artifacts
CFN_PARENT_TEMPLATE_FILE="deployment/aws/cloudformation/parent-stack.yaml"
CFN_PACKAGED_TEMPLATE_FILE="deployment/aws/cloudformation/nested-stacks.yaml"
CFN_PARAMETERS_FILE="deployment/aws/cloudformation/cfn-parameters.json"
TAG_NAME="Guillaume Bournique"
TAG_EMAIL="gbournique.dev1@gmail.com"
TAG_MODIFIED_DATE="$$(date +%F_%T)"

# Deployment
DOCKER_USER=gbournique
IMAGE_REPOSITORY=${DOCKER_USER}/tarikitchen
TAG=$(shell poetry version | awk '{print $$NF}')
DEBUG=False
CODEDEPLOY_APP_DIR=deployment/aws/codedeploy-app

# Database
RDS_POSTGRES_HOST=$$(echo "$$($(call get_stack_output, PostgresRdsEndpoint))")

# Load testing
WEBSERVER_URL=https://${STACK_NAME}.bournique.fr
USERS=100
SPAWN_RATE=50
RUN_TIME=1mn

>>>>>>> tari-kitchen
include utils/helpers.mk

### Environment and githooks ###
.PHONY: env env-update pre-commit

env:
	@ ${INFO} "Creating ${CONDA_ENV_NAME} conda environment and poetry dependencies"
	@ $(CONDA_CREATE) -f environment.yml -n $(CONDA_ENV_NAME)
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


### Development (CI) ###
.PHONY: runserver up tests cov clean

runserver:
	python app/manage.py collectstatic --no-input -v 0
	python app/manage.py makemigrations main
	python app/manage.py migrate --run-syncdb
	python app/manage.py runserver 0.0.0.0:8080

up:
	@ ${INFO} "Start webapp container"
	@ ./build_steps/ci.sh up

tests:
	@ ${INFO} "Run unit tests inside container"
	@ ./build_steps/ci.sh unit_tests

cov:
	@ ${INFO} "Open test coverage results"
	@ open htmlcov/index.html

clean:
	@ ${INFO} "Stopping and removing all containers"
	@ ./build_steps/ci.sh clean


### Terraform deployment (CD) ###
.PHONY: tf-deploy tf-destroy

tf-deploy:
	@ ${INFO} "Deploying application to a new ec2 instance with Terraform+Ansible"
	@ ${INFO} "For a production level deployment, use the cfn scripts in ./cd.sh"
	@ ./build_steps/cd.sh tf_launch
	@ ./build_steps/cd.sh tf_provision

tf-destroy:
	@ ./build_steps/cd.sh tf_destroy


### CI/CD scripts ###
.PHONY: ci-help cd-help

ci-help:
	@ ./build_steps/ci.sh || true

cd-help:
	@ ./build_steps/cd.sh || true
