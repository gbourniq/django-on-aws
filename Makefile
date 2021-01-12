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
STACK_NAME=myapp
AWS_DEFAULT_PROFILE=myaws
CFN_TEMPLATE_FILE="deployment/cfn-template-app.yaml"
CFN_PARAMETERS_FILE="deployment/cfn-template-parameters.json"
TAG_NAME="Guillaume Bournique"
TAG_EMAIL="gbournique.dev1@gmail.com"
TAG_MODIFIED_DATE="$$(date +%F_%T)"

# CodeDeploy
APP_CODE=deployment/sample-app

include utils/helpers.mk

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


### Docker image ###
.PHONY: image up healthcheck down publish
image:
	rm -rf dist
	poetry build
	docker build -t ${IMAGE_REPOSITORY}:$(TAG) .

up:
	@ ${INFO} "Running app with docker-compose (includes Postgres container)"
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
	@ ${INFO} "Running app as a standalone container"
	@ ${INFO} "Postgres host: ${POSTGRES_HOST}"
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


### Infrastructure ###
.PHONY: cfn-validate cfn-create cfn-update cfn-delete

cfn-validate:
	@ echo "Validating CloudFormation template ${CFN_TEMPLATE_FILE}"
	@ yamllint -d "{rules: {line-length: {max: 130, level: warning}}}" "${CFN_TEMPLATE_FILE}"
	@ cfn-lint "${CFN_TEMPLATE_FILE}"
	@ aws cloudformation validate-template --template-body file://"${CFN_TEMPLATE_FILE}" > /dev/null 2>&1

cfn-create: cfn-validate
	@ ${INFO} "Creating stack ${STACK_NAME}..."
	@ aws cloudformation create-stack \
		--stack-name=${STACK_NAME} \
		--template-body=file://"${CFN_TEMPLATE_FILE}" \
		--parameters=file://"${CFN_PARAMETERS_FILE}" \
		--tags "Key"="Name","Value"=\"${TAG_NAME}\" "Key"="Modified_Date","Value"="${TAG_MODIFIED_DATE}" "Key"="Email","Value"="${TAG_EMAIL}" \
		--profile=${AWS_DEFAULT_PROFILE} \
		--capabilities=CAPABILITY_NAMED_IAM
	@ echo "$$($(call wait_for_stack_creation_status))"

cfn-update: cfn-validate
	@ ${INFO} "Updating stack ${STACK_NAME}..."
	@ aws cloudformation update-stack \
		--stack-name=${STACK_NAME} \
		--template-body=file://"${CFN_TEMPLATE_FILE}" \
		--parameters=file://"${CFN_PARAMETERS_FILE}" \
		--tags "Key"="Name","Value"=\"${TAG_NAME}\" "Key"="Modified_Date","Value"="${TAG_MODIFIED_DATE}" "Key"="Email","Value"="${TAG_EMAIL}" \
		--profile=${AWS_DEFAULT_PROFILE} \
		--capabilities=CAPABILITY_NAMED_IAM
	@ echo "$$($(call wait_for_stack_update_status))"

cfn-delete:
	@ ${INFO} "Deleting stack ${STACK_NAME}..."
	@ aws cloudformation delete-stack --stack-name="${STACK_NAME}"
	@ echo "$$($(call wait_for_stack_delete_status))"


### Deployment ###
.PHONY: deploy deploy-push deploy-create deploy-get-status

deploy: deploy-push deploy-create deploy-get-status

deploy-push:
	@ ${INFO} "Push code to S3 and create a CodeDeploy application revision"
	@ aws deploy push \
		--application-name "$$($(call get_stack_output, CodeDeployApplicationName))" \
		--s3-location "s3://$$($(call get_stack_output, CodeDeployS3BucketName))/$$($(call codedeploy_app_name)).zip" \
		--source "${APP_CODE}" \
		--ignore-hidden-files

deploy-create:
	@ ${INFO} "Create deployment from the latest CodeDeploy application revision"
	@ aws deploy create-deployment \
		--application-name "$$($(call get_stack_output, CodeDeployApplicationName))" \
		--deployment-group-name "$$($(call get_stack_output, CodeDeployDeploymentGroupName))" \
		--s3-location "$$($(call codedeploy_s3_artifact))" \
		--description "Created by make deploy-create-deployment" \
		--file-exists-behavior OVERWRITE

deploy-get-status:
	@ ${INFO} "Check deployment status..."
	@ echo "$$($(call wait_for_codedeploy_deployment_status))"



