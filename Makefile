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
AWS_DEFAULT_PROFILE=myaws
ENVIRONMENT=prod
STACK_NAME=$(ENVIRONMENT)
S3_BUCKET_NAME_CFN_TEMPLATES=gbournique-sam-artifacts
CFN_PARENT_TEMPLATE_FILE="deployment/cloudformation/parent-stack.yaml"
CFN_PACKAGED_TEMPLATE_FILE="deployment/cloudformation/nested-stacks.yaml"
CFN_PARAMETERS_FILE="deployment/cloudformation/cfn-parameters.json"
TAG_NAME="Guillaume Bournique"
TAG_EMAIL="gbournique.dev1@gmail.com"
TAG_MODIFIED_DATE="$$(date +%F_%T)"

# CodeDeploy
APP_CODE=deployment/codedeploy-app

# AWS RDS Postgres as a DB backend (Note password must be stored securely)
POSTGRES_HOST=localhost
POSTGRES_PASSWORD=postgres
RDS_POSTGRES_HOST=$$(echo "$$($(call get_stack_output, PostgresRdsEndpoint))")

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
.PHONY: rundb stopdb recreatedb runserver tests open-cov-report

rundb:
	@ echo "Starting postgres container"
	@ docker-compose up -d postgres || true

stopdb:
	@ docker-compose down || true

recreatedb: rundb
	@ ${INFO} "Wiping portfoliodb table"
	docker exec -it --user=postgres postgres dropdb portfoliodb
	docker exec -it --user=postgres postgres createdb portfoliodb

runserver: rundb
	@ python app/manage.py migrate --run-syncdb
	@ python app/manage.py runserver 0.0.0.0:8080

tests: rundb
	@ ${INFO} "Running Django tests using the postgres container"
	@ pytest app -x
	@ docker-compose down || true
	@ ${INFO} "Run 'make open-cov-report' to view coverage details"

open-cov-report:
	@ open htmlcov/index.html

### Docker image ###
.PHONY: image up-with-local-db up healthcheck down publish
image:
	rm -rf dist
	poetry build
	docker build -t ${IMAGE_REPOSITORY}:$(TAG) .

up-local-db: rundb
	@ ${INFO} "Running app container, with local Postgres as a DB backend"
	@ docker run -d -p 8080:8080 --restart=no --network django-on-aws_backend ${IMAGE_REPOSITORY}:$(TAG)

up-rds-db: check-rds-connection
	@ ${INFO} "Running app container, with AWS RDS Postgres as a DB backend"
	@ ${INFO} "RDS postgres host: ${RDS_POSTGRES_HOST}"
	@ docker run -d \
				-p 8080:8080 \
				--restart=no \
				--env POSTGRES_HOST=${RDS_POSTGRES_HOST} \
				--env POSTGRES_PASSWORD=${RDS_POSTGRES_PASSWORD} \
				${IMAGE_REPOSITORY}:$(TAG)

check-rds-connection:
	@ [[ ! -z "${RDS_POSTGRES_HOST}" ]] || ${WARNING} "RDS_POSTGRES_HOST not set"
	@ [[ ! -z "${RDS_POSTGRES_PASSWORD}" ]] || ${WARNING} "RDS_POSTGRES_PASSWORD not set"
	@ echo "Check DB connection..."
	@ echo "User: postgres, Password: **** , Host: ${RDS_POSTGRES_HOST}, Database: portfoliodb"
	@ psql -d "postgresql://postgres:${RDS_POSTGRES_PASSWORD}@${RDS_POSTGRES_HOST}/portfoliodb" -c "select now()" > /dev/null

healthcheck:
	@ ${INFO} "Checking Django application container health"
	@ ./utils/healthcheck.sh ${IMAGE_REPOSITORY} ${TAG}

down:
	@ ${INFO} "Removing Django app container"
	@ docker rm --force $$(docker ps --filter "ancestor=${IMAGE_REPOSITORY}:$(TAG)" -qa)
	@ docker-compose down || true

publish:
	@ echo "${DOCKER_PASSWORD}" | docker login --username "${DOCKER_USER}" --password-stdin 2>&1
	@ docker push ${IMAGE_REPOSITORY}:$(TAG)


### Infrastructure ###
.PHONY: cfn-validate cfn-create cfn-update cfn-delete

cfn-package:
	@ ${INFO} "Packaging nested CloudFormation templates into ${CFN_PACKAGED_TEMPLATE_FILE}"
	@ aws cloudformation package \
		--template-file ${CFN_PARENT_TEMPLATE_FILE} \
		--output-template ${CFN_PACKAGED_TEMPLATE_FILE} \
		--s3-bucket ${S3_BUCKET_NAME_CFN_TEMPLATES}

cfn-validate: cfn-package
	@ ${INFO} "Validating CloudFormation template ${CFN_PACKAGED_TEMPLATE_FILE}"
	@ yamllint -d "{rules: {line-length: {max: 130, level: warning}}}" "${CFN_PACKAGED_TEMPLATE_FILE}"
	@ cfn-lint "${CFN_PACKAGED_TEMPLATE_FILE}"
	@ aws cloudformation validate-template --template-body file://"${CFN_PACKAGED_TEMPLATE_FILE}" > /dev/null

cfn-create: cfn-validate
	@ ${INFO} "Creating stack ${STACK_NAME}..."
	@ aws cloudformation create-stack \
		--stack-name=${STACK_NAME} \
		--template-body=file://"${CFN_PACKAGED_TEMPLATE_FILE}" \
		--parameters ParameterKey=ASGCPUTargetValue,ParameterValue=60 \
					 ParameterKey=ASGDesiredCapacity,ParameterValue=2 \
					 ParameterKey=CloudFrontExistingCertArn,ParameterValue=arn:aws:acm:us-east-1:164045463835:certificate/26654aed-53fe-4033-9866-9b072ad88ed8 \
					 ParameterKey=EC2LatestLinuxAmiId,ParameterValue=/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2 \
					 ParameterKey=EC2InstanceType,ParameterValue=t2.micro \
					 ParameterKey=EC2VolumeSize,ParameterValue=8 \
					 ParameterKey=Environment,ParameterValue=${ENVIRONMENT} \
					 ParameterKey=R53HostedZoneName,ParameterValue=bournique.fr \
					 ParameterKey=SSMParamSlackWebhookUrl,ParameterValue=/SLACK/INCOMING_WEBHOOK_URL \
					 ParameterKey=SSMParamNameRdsPostgresPassword,ParameterValue=/RDS/POSTGRES_PASSWORD/SECURE \
					 ParameterKey=SubnetListStr,ParameterValue=\"subnet-103a1a79\,subnet-28219264\" \
					 ParameterKey=VpcId,ParameterValue=vpc-e82c7280 \
		--tags "Key"="Name","Value"=\"${TAG_NAME}\" \
			   "Key"="Modified_Date","Value"="${TAG_MODIFIED_DATE}" \
			   "Key"="Email","Value"="${TAG_EMAIL}" \
		--profile=${AWS_DEFAULT_PROFILE} \
		--capabilities=CAPABILITY_NAMED_IAM
	@ echo "$$($(call wait_for_stack_creation_status))"

cfn-update: cfn-validate
	@ ${INFO} "Updating stack ${STACK_NAME}..."
	@ aws cloudformation update-stack \
		--stack-name=${STACK_NAME} \
		--template-body=file://"${CFN_PACKAGED_TEMPLATE_FILE}" \
		--parameters ParameterKey=ASGCPUTargetValue,ParameterValue=60 \
					 ParameterKey=ASGDesiredCapacity,ParameterValue=2 \
					 ParameterKey=CloudFrontExistingCertArn,ParameterValue=arn:aws:acm:us-east-1:164045463835:certificate/26654aed-53fe-4033-9866-9b072ad88ed8 \
					 ParameterKey=EC2LatestLinuxAmiId,ParameterValue=/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2 \
					 ParameterKey=EC2InstanceType,ParameterValue=t2.micro \
					 ParameterKey=EC2VolumeSize,ParameterValue=8 \
					 ParameterKey=Environment,ParameterValue=${ENVIRONMENT} \
					 ParameterKey=R53HostedZoneName,ParameterValue=bournique.fr \
					 ParameterKey=SSMParamSlackWebhookUrl,ParameterValue=/SLACK/INCOMING_WEBHOOK_URL \
					 ParameterKey=SSMParamNameRdsPostgresPassword,ParameterValue=/RDS/POSTGRES_PASSWORD/SECURE \
					 ParameterKey=SubnetListStr,ParameterValue=\"subnet-103a1a79\,subnet-28219264\" \
					 ParameterKey=VpcId,ParameterValue=vpc-e82c7280 \
		--tags "Key"="Name","Value"=\"${TAG_NAME}\" \
			   "Key"="Modified_Date","Value"="${TAG_MODIFIED_DATE}" \
			   "Key"="Email","Value"="${TAG_EMAIL}" \
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
	aws deploy create-deployment \
		--application-name "$$($(call get_stack_output, CodeDeployApplicationName))" \
		--deployment-group-name "$$($(call get_stack_output, CodeDeployDeploymentGroupName))" \
		--s3-location "$$($(call codedeploy_s3_artifact))" \
		--description "Created by make deploy-create-deployment" \
		--file-exists-behavior OVERWRITE

deploy-get-status:
	@ ${INFO} "Check deployment status..."
	@ echo "$$($(call wait_for_codedeploy_deployment_status))"
