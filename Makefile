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

### Infrastructure ###
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
deploy-push:
	@ ${INFO} "Push code to S3 and create an application revision"
	@ aws deploy push \
		--application-name "$$($(call codedeploy_app_name))" \
		--s3-location "s3://$$($(call codedeploy_bucket_name))/$$($(call codedeploy_app_name)).zip" \
		--source "${APP_CODE}" \
		--ignore-hidden-files

deploy-create:
	@ ${INFO} "Create deployment from the latest CodeDeploy application revision"
	@ aws deploy create-deployment \
		--application-name "$$($(call codedeploy_app_name))" \
		--s3-location bucket="$$($(call codedeploy_bucket_name))",key="$$($(call codedeploy_s3_key_name))",bundleType=zip,eTag="$$($(call codedeploy_s3_key_eTag))",version="$$($(call codedeploy_s3_key_version))" \
		--deployment-group-name "$$($(call codedeploy_deployment_group_name))" \
		--description "Created by make deploy-create-deployment" \
		--file-exists-behavior OVERWRITE

deploy-get-status:
	@ ${INFO} "Check deployment status..."
	@ echo "$$($(call wait_for_codedeploy_deployment_status))"

deploy: deploy-push deploy-create deploy-get-status

### Helpers ###

# CloudFormation
define get_stack_status
aws cloudformation describe-stacks --stack-name=${STACK_NAME} | jq -r '.Stacks[0].StackStatus'
endef

wait_for_stack_creation_status = { \
  until [[ "$$($(call get_stack_status))" != "CREATE_IN_PROGRESS" ]]; \
    do sleep 5; \
  done; \
  if [[ "$$($(call get_stack_status))" != "CREATE_COMPLETE" ]]; \
    then echo "Oops, something went wrong during stack creation ❌"; exit 1; \
  fi; \
  echo "Stack creation completed! ✅"; \
}

wait_for_stack_update_status = { \
  until [[ "$$($(call get_stack_status))" != "UPDATE_IN_PROGRESS" ]]; \
    do sleep 5; \
  done; \
  if [[ "$$($(call get_stack_status))" != "UPDATE_COMPLETE" ]]; \
    then echo "Oops, something went wrong during stack update ❌"; exit 1; \
  fi; \
  echo "Stack update completed! ✅"; \
}

wait_for_stack_delete_status = { \
  until [[ "$$($(call get_stack_status))" != "DELETE_IN_PROGRESS" ]]; \
    do sleep 5; \
  done; \
  echo "Stack delete completed! ✅"; \
}

define codedeploy_app_name
aws cloudformation describe-stacks \
	--stack-name ${STACK_NAME} \
	--query 'Stacks[].Outputs[?OutputKey==`CodeDeployApplicationName`].OutputValue' \
	--output text
endef

define codedeploy_deployment_group_name
aws cloudformation describe-stacks \
	--stack-name ${STACK_NAME} \
	--query 'Stacks[].Outputs[?OutputKey==`CodeDeployDeploymentGroupName`].OutputValue' \
	--output text
endef

define codedeploy_bucket_name
aws cloudformation describe-stacks \
	--stack-name ${STACK_NAME} \
	--query 'Stacks[].Outputs[?OutputKey==`CodeDeployS3BucketName`].OutputValue' \
	--output text
endef

define codedeploy_s3_key_name
aws deploy list-application-revisions --application-name "$$($(call codedeploy_app_name))" --query "revisions[].s3Location[].key" --sort-by registerTime --sort-order descending --max-items 1 | jq '.[]' | sed 's/\"//g'
endef

define codedeploy_s3_key_version
aws deploy list-application-revisions --application-name "$$($(call codedeploy_app_name))" --query "revisions[].s3Location[].version" --sort-by registerTime --sort-order descending --max-items 1 | jq '.[]' | sed 's/\"//g'
endef

define codedeploy_s3_key_eTag
aws deploy list-application-revisions --application-name "$$($(call codedeploy_app_name))" --query "revisions[].s3Location[].eTag" --sort-by registerTime --sort-order descending --max-items 1 | jq '.[]' | sed 's/\"//g'
endef

define codedeploy_latest_deployment_id
aws deploy list-deployments --application-name "$$($(call codedeploy_app_name))" --deployment-group-name "$$($(call codedeploy_deployment_group_name))" --query "deployments" --max-items 1 | jq '.[]' | sed 's/\"//g'
endef

define deployment_status
aws deploy get-deployment --deployment-id $$($(call codedeploy_latest_deployment_id)) --query "deploymentInfo.status"
endef

wait_for_codedeploy_deployment_status = { \
  until [[ "$$($(call deployment_status))" != '"InProgress"' ]]; \
    do sleep 1; \
  done; \
  if [[ "$$($(call deployment_status))" != '"Succeeded"' ]]; \
    then echo "Deployment failed"; exit 1; \
  fi; \
  echo "Deployment succeeded!"; \
}

# Cosmetics
RED := "\e[1;31m"
YELLOW := "\e[1;33m"
GREEN := "\033[32m"
NC := "\e[0m"
INFO := @bash -c 'printf ${YELLOW}; echo "[INFO] $$1"; printf ${NC}' MESSAGE
MESSAGE := @bash -c 'printf ${NC}; echo "$$1"; printf ${NC}' MESSAGE
SUCCESS := @bash -c 'printf ${GREEN}; echo "[SUCCESS] $$1"; printf ${NC}' MESSAGE
WARNING := @bash -c 'printf ${RED}; echo "[WARNING] $$1"; printf ${NC}' MESSAGEs