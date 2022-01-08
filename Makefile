# Oneshell means I can run multiple lines in a recipe in the same shell, so I don't have to
# chain commands together with semicolon
.ONESHELL:

# Set shell
SHELL=/bin/bash

# Conda environment
CONDA_ENV_NAME=django-on-aws
CONDA_CREATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda env create
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate

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
.PHONY: build start_db runserver up tests cov clean

build:
	@ ${INFO} "Build CI and webapp images"
	@ ./build_steps/ci.sh build

start_db:
	@ ${INFO} "Start databases containers"
	@ ./build_steps/ci.sh start_db

runserver:
	POSTGRES_HOST=localhost REDIS_ENDPOINT=localhost:6379 python app/manage.py collectstatic --no-input -v 0
	POSTGRES_HOST=localhost REDIS_ENDPOINT=localhost:6379 python app/manage.py makemigrations main
	POSTGRES_HOST=localhost REDIS_ENDPOINT=localhost:6379 python app/manage.py migrate --run-syncdb
	POSTGRES_HOST=localhost REDIS_ENDPOINT=localhost:6379 DJANGO_SUPERUSER_PASSWORD=test python app/manage.py createsuperuser --username test --email gbournique@gmail.com --noinput || true
	POSTGRES_HOST=localhost REDIS_ENDPOINT=localhost:6379 python app/manage.py runserver 0.0.0.0:8080

up:
	@ ${INFO} "Start databases and webapp containers"
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
.PHONY: ci-help cd-help ci-all cd-all

ci-help:
	@ ./build_steps/ci.sh || true

cd-help:
	@ ./build_steps/cd.sh || true

ci-all:
	@ ${INFO} "Running the CI pipeline build steps locally"
	./build_steps/ci.sh build
	./build_steps/ci.sh start_db
	./build_steps/ci.sh unit_tests
	./build_steps/ci.sh lint
	./build_steps/ci.sh healthcheck
	./build_steps/ci.sh clean
	./build_steps/ci.sh push_images
	./build_steps/ci.sh put_ssm_vars

cd-all:
	@ ${INFO} "Running the CD pipeline build steps locally"
	CFN_STACK_NAME=demo R53_SUB_DOMAIN=True ./build_steps/cd.sh cfn_create
	CFN_STACK_NAME=demo ./build_steps/cd.sh code_deploy
	CFN_STACK_NAME=demo R53_SUB_DOMAIN=True ./build_steps/cd.sh cfn_update
	CFN_STACK_NAME=demo R53_SUB_DOMAIN=True ./build_steps/cd.sh load_testing
	CFN_STACK_NAME=demo ./build_steps/cd.sh cfn_destroy_async

backup:
	CFN_STACK_NAME="live" R53_SUB_DOMAIN=False S3_DATA_BACKUP_URI="s3://gbournique-artefacts/tari.kitchen-backups" ./build_steps/cd.sh create_backup