# Set shell
SHELL=/bin/bash -e -o pipefail

### Environment variables ###
CONDA_ENV_NAME=django-on-aws
CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate
# S3_BUCKET_NAME=gbournique-s3-sam-builds
VERSION=$(shell poetry version | awk '{print $$NF}')


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


### Build dependencies ###


### Testing ###
.PHONY: start-django-server

# For quick manual testing during development
start-django-server:
	@ python app/manage.py runserver 0.0.0.0:8080

# tests:
# 	@ ${INFO} "Running tests using the FastAPI Test client"
# 	@ pytest .
# 	@ ${INFO} "Run 'make open-cov-report' to view coverage details"

# open-cov-report:
# 	@ open htmlcov/index.html


### Deployment ###


### Clean up ###


### Helpers ###


### Fancy colours ###
RED := "\e[1;31m"
YELLOW := "\e[1;33m"
GREEN := "\033[32m"
NC := "\e[0m"
INFO := @bash -c 'printf ${YELLOW}; echo "[INFO] $$1"; printf ${NC}' MESSAGE
MESSAGE := @bash -c 'printf ${NC}; echo "$$1"; printf ${NC}' MESSAGE
SUCCESS := @bash -c 'printf ${GREEN}; echo "[SUCCESS] $$1"; printf ${NC}' MESSAGE
WARNING := @bash -c 'printf ${RED}; echo "[WARNING] $$1"; printf ${NC}' MESSAGEs