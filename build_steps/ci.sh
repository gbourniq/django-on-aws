#!/usr/bin/env bash

# -e: Exit on first failure
# -E (-o errtrace): Ensures that ERR traps get inherited by functions and subshells.
# -u (-o nounset): Treats unset variables as errors.
# -o pipefail: This option will propagate intermediate errors when using pipes.
set -Eeo pipefail
# set -ex

script_name="$(basename -- "$0")"
script_dir="$(dirname "$0")"

trap err_exit ERR

err_exit () {
	echo "echo ⚠️ Something went wrong! Tidying up..."
	stop_db
	down
	exit 1
}

help_text()
{
    echo ""
    echo "Helper script to run and manage the scripts invoked by the CI pipeline."
    echo ""
    echo "⚠️  This must be run from the root of the repository."
    echo ""
    echo "Usage:        $script_dir/$script_name COMMAND"
    echo ""
    echo "Available Commands:"
    echo "  build               🔨 Build ci and webapp docker images"
    echo "  start_db            🟢 Start redis and postgres containers"
    echo "  stop_db             🔴 Stop redis and postgres containers"
    echo "  up                  🆙 Start webapp container"
    echo "  unit_tests          🕵 Run unit tests"
    echo "  lint                ✨ Run pre-commit hooks (linting)"
    echo "  healthcheck         🚑 Check webapp container health"
    echo "  push_images         🐳 Publish images to Dockerhub"
    echo "  put_ssm_vars        ☁️ Update AWS ssm parameters"
}

check_required_env_variables()
{
	var_not_set() {
		echo "❌ Environment variable not set: $1" 1>&2
		exit 1
	}
    if [[ ! $AWS_DEFAULT_REGION || ! $AWS_ACCESS_KEY_ID || ! $AWS_SECRET_ACCESS_KEY ]]; then
        var_not_set "AWS_DEFAULT_REGION; AWS_ACCESS_KEY_ID; AWS_SECRET_ACCESS_KEY"
    fi
    if [[ ! $DOCKER_PASSWORD ]]; then
        var_not_set "DOCKER_PASSWORD"
    fi
}

set_common_env_variables()
{
	# Docker (experimental cli to use docker manifest)
	export DOCKER_USER=gbournique
    export DOCKER_CLI_EXPERIMENTAL=enabled

	# CI/CD docker image
	export CI_IMAGE_REPOSITORY=${DOCKER_USER}/cicd-with-deps

	# Webapp docker image
	export DEPLOYMENT_DIR="./deployment/"
	export WEBAPP_IMAGE_REPOSITORY=${DOCKER_USER}/django-on-aws
	export WEBAPP_CONTAINER_NAME=webapp
	export DEBUG=False

	check_required_env_variables
}

docker-ci() {
	docker network create global-network 2>/dev/null || true; \
	docker run \
		-it --rm \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(pwd):/root/cicd/ \
		--network global-network \
		-e AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION} \
		-e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
		-e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
		${CI_IMAGE_REPOSITORY}:$(ci_image_tag) bash -c "$*"
}

ci_image_tag() {
	echo $(cat ./build_steps/cicd.Dockerfile environment.yml poetry.lock | cksum | cut -c -8)
}

build_ci_image() {
	printf "Building ci docker image ${CI_IMAGE_REPOSITORY}:$(ci_image_tag)...\n"
	if docker manifest inspect ${CI_IMAGE_REPOSITORY}:$(ci_image_tag) >/dev/null 2>&1; then
		echo Docker image ${CI_IMAGE_REPOSITORY}:$(ci_image_tag) already exists on Dockerhub! Not building.
		docker pull ${CI_IMAGE_REPOSITORY}:$(ci_image_tag)
	else \
		docker build -t ${CI_IMAGE_REPOSITORY}:$(ci_image_tag) -f ./build_steps/cicd.Dockerfile .
	fi
}

webapp_image_tag() {
	WEBAPP_DEPENDENCIES_FILES=$(echo $(find ./app -type f -not -name "*.pyc" -not -name "*.log") \
								"./deployment/webapp.Dockerfile" "environment.yml" "poetry.lock")
	CKSUM=$(cat ${WEBAPP_DEPENDENCIES_FILES} | cksum | cut -c -8)
	PROJECT_VERSION=$(awk '/^version/' pyproject.toml | sed 's/[^0-9\.]//g')
	echo ${PROJECT_VERSION}-${CKSUM}
}

build_webapp_image() {
	printf "Building webapp docker image ${WEBAPP_IMAGE_REPOSITORY}:$(webapp_image_tag)...\n"
	if docker manifest inspect ${WEBAPP_IMAGE_REPOSITORY}:$(webapp_image_tag) >/dev/null 2>&1; then
		echo Docker image ${WEBAPP_IMAGE_REPOSITORY}:$(webapp_image_tag) already exists on Dockerhub! Not building.
		docker pull ${WEBAPP_IMAGE_REPOSITORY}:$(webapp_image_tag)
	else \
		rm -rf dist
		docker-ci poetry build
		docker build -t ${WEBAPP_IMAGE_REPOSITORY}:$(webapp_image_tag) -f ./deployment/webapp.Dockerfile .
	fi
}

start_db()
{
	docker-ci "cd ${DEPLOYMENT_DIR}; docker-compose up -d" || true
}

stop_db()
{
	docker-ci "cd ${DEPLOYMENT_DIR}; docker-compose down --remove-orphans" >/dev/null 2>&1 || true
}

unit_tests()
{
	docker-ci "pytest app -x; coverage-badge -o .github/coverage.svg -f"
}

lint()
{
	docker-ci pre-commit run --all-files --show-diff-on-failure
}

up()
{
	docker-ci docker run -d --name ${WEBAPP_CONTAINER_NAME} -p 8080:8080 --restart=no \
			  		 	 --network global-network \
						 --env DEBUG=True \
						 --env POSTGRES_HOST=postgres \
						 --env POSTGRES_PASSWORD=postgres \
						 --env REDIS_ENDPOINT=redis:6379 \
						 --env SNS_TOPIC_ARN= \
						 --env SES_IDENTITY_ARN= \
						 ${WEBAPP_IMAGE_REPOSITORY}:$(webapp_image_tag) || true; \
}

down()
{
	docker-ci docker rm --force $(docker ps --filter name=${WEBAPP_CONTAINER_NAME} -qa) >/dev/null 2>&1 || true
}

healthcheck()
{
	get_service_health() {
		echo "$1" | xargs -I ID docker inspect -f '{{if .State.Running}}{{ .State.Health.Status }}{{end}}' ID
	}

	container_id=$(docker ps --filter name=$1 -qa)

	# Check if container exists
	if [[ -z "${container_id}" ]]; then
		echo "❌ Container $1 is not running.. Aborting!"
		exit 1
	fi;

	# Wait for the container to fully start up
	until [[ $(get_service_health "${container_id}") != "starting" ]]; do
		sleep 1
	done;

	# Check if container status shows healthy
	if [[ $(get_service_health "${container_id}") != "healthy" ]]; then
		echo "❌ $1 failed health check"
		exit 1
	fi;

	echo "🍀 Container $1 is healthy"
}

publish_image()
{
	echo ${DOCKER_PASSWORD} | docker login --username ${DOCKER_USER} --password-stdin 2>&1
	printf "Publishing $1:$2...\n"
	docker push $1:$2
	docker tag $1:$2 $1:latest
	docker push $1:latest
}

put_ssm_parameter_str()
{
	printf "Updating parameter '$1' with value '$2'\n"
	docker-ci aws ssm put-parameter \
				  --name $1 \
				  --value $2 \
				  --type "String" \
				  --overwrite >/dev/null; \
}

# Script starting point
if [[ -n $1 ]]; then
	case "$1" in
		build)
			printf "🔨 Building ci and webapp docker images...\n"
			set_common_env_variables
			build_ci_image
			build_webapp_image
			exit 0
			;;
		start_db)
			printf "🐳 Starting redis and postgres containers...\n"
			set_common_env_variables
			start_db
			exit 0
			;;
		stop_db)
			printf "🔥🚒 Stopping redis and postgres containers...\n"
			set_common_env_variables
			stop_db
			exit 0
			;;
		up)
			printf "🐳 Starting webapp container...\n"
			set_common_env_variables
			start_db
			up
			exit 0
			;;
		unit_tests)
			printf "🔎🕵 Running unit tests...\n"
			set_common_env_variables
			start_db
			unit_tests
			stop_db
			exit 0
			;;
		lint)
			printf "🚨✨ Running pre-commit hooks (linting)...\n"
			set_common_env_variables
			lint
			exit 0
			;;
		healthcheck)
			printf "👨‍⚕🚑 Checking webapp container health...\n"
			set_common_env_variables
			start_db
			up
			healthcheck ${WEBAPP_CONTAINER_NAME}
			down
			stop_db
			exit 0
			;;
		clean)
			printf "🧹 Stopping and removing all containers...\n"
			set_common_env_variables
			stop_db
			down
			exit 0
			;;
		push_images)
			printf "🐳 Publishing images to Dockerhub...\n"
			set_common_env_variables
			publish_image ${WEBAPP_IMAGE_REPOSITORY} $(webapp_image_tag)
			publish_image ${CI_IMAGE_REPOSITORY} $(ci_image_tag)
			exit 0
			;;
		put_ssm_vars)
			printf "☁️ Updating AWS ssm parameters...\n"
			set_common_env_variables
			put_ssm_parameter_str "/CODEDEPLOY/DOCKER_IMAGE_NAME" "${WEBAPP_IMAGE_REPOSITORY}:$(webapp_image_tag)"
			put_ssm_parameter_str "/CODEDEPLOY/DEBUG_DEMO" "${DEBUG}"
			exit 0
			;;
		*)
			echo "¯\\_(ツ)_/¯ What do you mean \"$1\"?"
			help_text
			exit 1
			;;
	esac
else
	help_text
	exit 1
fi
