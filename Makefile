# Set shell
SHELL=/bin/bash -e -o pipefail

### Environment variables ###
CONDA_ENV_NAME=django-on-aws
CONDA_CREATE=source ${HOME}/miniconda/etc/profile.d/conda.sh ; conda env create
CONDA_ACTIVATE=source ${HOME}/miniconda/etc/profile.d/conda.sh ; conda activate

# Cloudformation
AWS_DEFAULT_PROFILE=myaws
ENVIRONMENT=dev
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
IMAGE_REPOSITORY=${DOCKER_USER}/django-on-aws
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

include utils/helpers.mk

### Environment and pre-commit hooks ###
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


### Development and Testing ###
.PHONY: rundb stopdb recreatedb runserver tests open-cov-report

rundb:
	@ echo "Starting postgres container"
	@ docker-compose up -d || true

stopdb:
	@ docker-compose down || true

recreatedb: rundb
	@ ${INFO} "Wiping portfoliodb table"
	docker exec -it --user=postgres postgres dropdb portfoliodb
	docker exec -it --user=postgres postgres createdb portfoliodb

runserver: rundb
	python app/manage.py collectstatic --no-input -v 0
	python app/manage.py makemigrations main
	python app/manage.py migrate --run-syncdb
	python app/manage.py runserver 0.0.0.0:8080

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

up: rundb
	@ ${INFO} "Running app container, with local Postgres as a DB backend and Redis for Cache"
	@ docker run -d \
				-p 8080:8080 \
				--restart=no \
				--network django-on-aws_backend \
				--env DEBUG=True \
				--env POSTGRES_HOST=postgres \
				--env POSTGRES_PASSWORD=postgres \
				--env REDIS_ENDPOINT=redis:6379 \
				--env SNS_TOPIC_ARN="" \
				${IMAGE_REPOSITORY}:$(TAG)

healthcheck:
	@ ${INFO} "Checking Django application container health"
	@ ./utils/healthcheck.sh ${IMAGE_REPOSITORY} ${TAG}

down:
	@ ${INFO} "Removing Django app container"
	@ docker rm --force $$(docker ps --filter "ancestor=${IMAGE_REPOSITORY}:$(TAG)" -qa) || true
	@ docker-compose down || true

publish:
	@ [[ ! -z "${DOCKER_PASSWORD}" ]] || ${WARNING} "DOCKER_PASSWORD not set"
	@ [[ ! -z "${DOCKER_USER}" ]] || ${WARNING} "DOCKER_USER not set"
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

deploy: put-image-name-to-ssm deploy-push deploy-create deploy-get-status

put-image-name-to-ssm:
	@ ${INFO} "Starting deployment of docker image ${IMAGE_REPOSITORY}:$(TAG) (DEBUG=${DEBUG})"
	@ aws ssm put-parameter \
		--name "/CODEDEPLOY/DOCKER_IMAGE_NAME" \
		--type "String" \
		--value "${IMAGE_REPOSITORY}:$(TAG)" \
		--overwrite >/dev/null
	@ aws ssm put-parameter \
		--name "/CODEDEPLOY/DEBUG" \
		--type "String" \
		--value "${DEBUG}" \
		--overwrite >/dev/null

deploy-push:
	@ ${INFO} "Push code to S3 and create a CodeDeploy application revision"
	@ aws deploy push \
		--application-name "$$($(call get_stack_output, CodeDeployApplicationName))" \
		--s3-location "s3://$$($(call get_stack_output, CodeDeployS3BucketName))/$$($(call codedeploy_app_name)).zip" \
		--source "${CODEDEPLOY_APP_DIR}" \
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


# Load Testing
load-testing:
	@ ${INFO} "Load testing ${WEBSERVER_URL} by spawning ${USERS} users (${SPAWN_RATE}/s) for ${RUN_TIME} minutes."
	@ locust -f utils/locustfile.py \
		--host ${WEBSERVER_URL} \
		--headless --users ${USERS} --spawn-rate ${SPAWN_RATE} --run-time ${RUN_TIME} --only-summary

load-testing-ui:
	@ ${INFO} "Starting load testing UI"
	@ locust -f utils/locustfile.py --host ${WEBSERVER_URL}