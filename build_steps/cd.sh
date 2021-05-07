#!/usr/bin/env bash

# -e: Exit on first failure
# -E (-o errtrace): Ensures that ERR traps get inherited by functions and subshells.
# -u (-o nounset): Treats unset variables as errors.
# -o pipefail: This option will propagate intermediate errors when using pipes.
set -Eeuo pipefail
# set -ex

script_name="$(basename -- "$0")"
script_dir="$(dirname "$0")"

trap err_exit ERR

err_exit () {
	echo "echo ⚠️ Something went wrong! Tidying up..."
	exit 1
}

help_text()
{
    echo ""
    echo "Helper script to run and manage the scripts invoked by the CD pipeline."
    echo ""
    echo "⚠️  This must be run from the root of the repository."
    echo ""
    echo "Usage:        $script_dir/$script_name COMMAND"
    echo ""
    echo "Available Commands:"
    echo "  tf_launch           🚀 Run Terraform to launch new instance(s)"
    echo "  tf_provision        👷‍♂️ Run Terraform+Ansible to git clone repo and start webapp on new instance(s)"
    echo "  tf_destroy          💥 Run Terraform to destroy instance(s) and created resource(s)"
    echo "  cfn_create          👷‍♂️ Run Cloudformation to create AWS infrastructure (production level)"
    echo "  cfn_update          🔃 Run Cloudformation to update AWS infrastructure"
    echo "  cfn_destroy         💥 Run Cloudformation to destroy AWS infrastructure"
    echo "  cfn_destroy_async   ⏳ Run Cloudformation to destroy AWS infrastructure (async call)"
	echo "  code_deploy         🚚 Run AWS CodeDeploy to deploy application to launched instances"
    echo "  load_testing        📈 Run load testing on deployed web application"
    echo "  load_testing_ui     📈 Start UI for load testing on deployed web application"
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
}

set_common_env_variables()
{
	# Docker (experimental cli to use docker manifest)
	export DOCKER_USER=gbournique

	# Image which contains required cli packages such as awscli, terraform, etc.
	export CD_IMAGE=${DOCKER_USER}/cicd-with-deps:19590890

	# Terraform
	export TF_DIR=./deployment/dev/terraform
	export TF_LOG_PATH=./terraform-crash.log
	export TF_LOG=TRACE

	# Ansible
	export ANSIBLE_DIR=./deployment/dev/ansible
	export ANSIBLE_HOST_KEY_CHECKING=False
	export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible_vault_pass
	export ANSIBLE_GIT_REPO_NAME=django-on-aws
	export ANSIBLE_GIT_BRANCH_NAME=main

	# Cloudformation
	export CFN_STACK_NAME=demo
	export CFN_TEMPLATES_S3_BUCKET_NAME=gbournique-sam-artifacts
	export CFN_DIR="./deployment/prod/cloudformation/"
	export CFN_PARENT_TEMPLATE_FILE="${CFN_DIR}/parent-stack.yaml"
	export CFN_PACKAGED_TEMPLATE_FILE="${CFN_DIR}/nested-stacks.yaml"
	export CFN_PARAMETERS_FILE="${CFN_DIR}/parameters.json"
	export CFN_TAG_NAME="Guillaume Bournique"
	export CFN_TAG_EMAIL="gbournique.dev1@gmail.com"
	export CFN_TAG_MODIFIED_DATE="$(date +%F_%T)"

	# CodeDeploy
	export CODEDEPLOY_APP_DIR="./deployment/prod/codedeploy-app"
	export STACK_OUTPUT_APP_NAME="CodeDeployApplicationName"
	export STACK_OUTPUT_CODEDEPLOY_GROUP_NAME="CodeDeployDeploymentGroupName"
	export STACK_OUTPUT_CODEDEPLOY_S3_BUCKET_NAME="CodeDeployS3BucketName"

	# Load testing
	export WEBSERVER_URL=https://${CFN_STACK_NAME}.bournique.fr
	export USERS=100
	export SPAWN_RATE_PS=50
	export RUN_TIME=1mn

	check_required_env_variables
}

# To run command within a container which has all required packages installed
docker-cd() {
	docker run \
		-it --rm \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(pwd):/root/cicd/ \
		-e AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION} \
		-e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
		-e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
		-e TF_LOG_PATH=${TF_LOG_PATH} \
		-e TF_LOG=${TF_LOG} \
		${CD_IMAGE} bash -c "$*"
}

# Terraform + Ansible related functions
tf_launch() {
	cd ${TF_DIR}
	terraform init
	terraform fmt -recursive
	terraform validate
	terraform plan -out=./.terraform/terraform_plan
	terraform apply ./.terraform/terraform_plan
}

tf_provision() {
	python_version=$(python -V | sed 's/[^0-9\.]//g')
	ansible-playbook -i "${ANSIBLE_DIR}/inventories" "${ANSIBLE_DIR}/staging.yaml" -vv --timeout 60
}

tf_destroy() {
	cd ${TF_DIR}
	terraform destroy --auto-approve
}


# Cloudformation related functions
cfn_package() {

	# Packaging nested CloudFormation templates
	docker-cd aws cloudformation package \
		--template-file ${CFN_PARENT_TEMPLATE_FILE} \
		--output-template ${CFN_PACKAGED_TEMPLATE_FILE} \
		--s3-bucket ${CFN_TEMPLATES_S3_BUCKET_NAME}

	# Validating CloudFormation template
	docker-cd aws cloudformation validate-template --template-body file://${CFN_PACKAGED_TEMPLATE_FILE} > /dev/null

	# The stack name (dev/demo) is used as the subdomain name, eg. demo.mydomain.com
	# If set to 'demo', then an RDS database snapshot will be created on stack deletion 
	docker-cd aws ssm put-parameter \
		--name /DEPLOYMENT/ENVIRONMENT \
		--value ${CFN_STACK_NAME} \
		--type "String" --overwrite >/dev/null
}

cfn_create() {
	docker-cd aws cloudformation create-stack \
		--stack-name=${CFN_STACK_NAME} \
		--template-body=file://"${CFN_PACKAGED_TEMPLATE_FILE}" \
		--parameters file://"${CFN_PARAMETERS_FILE}" \
		--tags "Key"="Name","Value"=\"${CFN_TAG_NAME}\" \
			   "Key"="Modified_Date","Value"="${CFN_TAG_MODIFIED_DATE}" \
			   "Key"="Email","Value"="${CFN_TAG_EMAIL}" \
		--capabilities=CAPABILITY_NAMED_IAM
}

cfn_update() {
	docker-cd aws cloudformation update-stack \
		--stack-name=${CFN_STACK_NAME} \
		--template-body=file://"${CFN_PACKAGED_TEMPLATE_FILE}" \
		--parameters file://"${CFN_PARAMETERS_FILE}" \
		--tags "Key"="Name","Value"=\"${CFN_TAG_NAME}\" \
			   "Key"="Modified_Date","Value"="${CFN_TAG_MODIFIED_DATE}" \
			   "Key"="Email","Value"="${CFN_TAG_EMAIL}" \
		--capabilities=CAPABILITY_NAMED_IAM
}

cfn_destroy() {
	docker-cd aws cloudformation delete-stack --stack-name=${CFN_STACK_NAME}
}

wait_for_stack_status() {

	status_in_progress=$1
	status_complete=$2

	get_stack_status() {
		status=$(docker-cd aws cloudformation describe-stacks \
				--stack-name=${CFN_STACK_NAME} | jq -r '.Stacks[0].StackStatus' 2>/dev/null || true)
		if [[ -z $status ]]; then
			# empty status, i.e stack does not exist (likely deleted)
			echo "empty_status"
		else
			echo $status
		fi;
	}

	until [[ $(get_stack_status) != $status_in_progress ]];
	do
		echo "🕵️‍♂️  Current status: $status_in_progress..."
		sleep 30
	done

	until [[ $(get_stack_status) != "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS" ]];
	do
		echo "🕵️‍♂️  Clean up operation in progress (UPDATE_COMPLETE_CLEANUP_IN_PROGRESS)..."
		sleep 30
	done

	if [[ $status_complete == $(get_stack_status) || $status_complete == "DELETE_COMPLETE" ]]; then
		# Expected complete status was reached, or
		# Stack Deletion case: could not retrieve status because the stack does not exist (deleted). All good.
		echo "✅  Complete!"
		exit 0
	fi

	echo "❌  Oops, something went wrong!"
	exit 1
}


# CodeDeploy related functions
get_stack_output() {
	echo $(docker-cd aws cloudformation describe-stacks \
						--stack-name demo \
						--output json | jq -r ".Stacks[0].Outputs \
												| map({key: .OutputKey, value: .OutputValue}) \
												| from_entries \
												| .$1")
}

code_deploy_push() {
	echo "Push code to S3 and create a CodeDeploy application revision"

	codedeploy_app_name=$(get_stack_output "$STACK_OUTPUT_APP_NAME")
	s3_bucket_name=$(get_stack_output "$STACK_OUTPUT_CODEDEPLOY_S3_BUCKET_NAME")

	docker-cd aws deploy push \
		--application-name $codedeploy_app_name \
		--s3-location "s3://$s3_bucket_name/$codedeploy_app_name.zip" \
		--source ${CODEDEPLOY_APP_DIR} \
		--ignore-hidden-files
}

code_deploy_create() {

	get_codedeploy_revision_attribute() {
		echo $(docker-cd aws deploy list-application-revisions \
							--application-name $(get_stack_output $STACK_OUTPUT_APP_NAME) \
							--query "revisions[].s3Location[].$1" \
							--sort-by registerTime \
							--sort-order descending \
							--max-items 1 | jq '.[]' | sed 's/\"//g')
	}

	codedeploy_artifact_s3_location=$(echo "bucket=$(get_stack_output $STACK_OUTPUT_CODEDEPLOY_S3_BUCKET_NAME),\
											key=$(get_codedeploy_revision_attribute key),\
											bundleType=zip,\
											eTag=$(get_codedeploy_revision_attribute eTag),\
											version=$(get_codedeploy_revision_attribute version)" | sed 's/[[:space:]]*//g')

	docker-cd aws deploy create-deployment \
					--application-name $(get_stack_output $STACK_OUTPUT_APP_NAME) \
					--deployment-group-name $(get_stack_output $STACK_OUTPUT_CODEDEPLOY_GROUP_NAME) \
					--s3-location "$codedeploy_artifact_s3_location" \
					--description "Created-by-GB" \
					--file-exists-behavior OVERWRITE
}

wait_for_codedeploy_status() {

	status_in_progress=$1
	status_complete=$2

	get_codedeploy_deployment_status() {
		latest_deployment_id=$(aws deploy list-deployments \
										--application-name $(get_stack_output $STACK_OUTPUT_APP_NAME) \
										--deployment-group-name $(get_stack_output $STACK_OUTPUT_CODEDEPLOY_GROUP_NAME) \
										--query "deployments" \
										--max-items 1 | jq '.[]' | sed 's/\"//g')
		echo $(aws deploy get-deployment --deployment-id $latest_deployment_id --query "deploymentInfo.status")
	}

	until [[ $(get_codedeploy_deployment_status) != $status_in_progress ]];
	do
		echo "🕵️‍♂️  Current status: $status_in_progress..."
		sleep 30
	done

	if [[ $status_complete == $(get_codedeploy_deployment_status) ]]; then
		echo "✅  Complete!"
		exit 0
	fi

	echo "❌  Oops, something went wrong!"
	exit 1
}


# Load testing related functions
load_testing() {
	echo "Load testing ${WEBSERVER_URL} by spawning ${USERS} users \
		  at a rate of ${SPAWN_RATE_PS}/s and maintain a full load for ${RUN_TIME} minutes."
	docker-ci locust -f utils/locustfile.py \
		--host ${WEBSERVER_URL} \
		--headless --users ${USERS} \
		--spawn-rate ${SPAWN_RATE_PS} \
		--run-time ${RUN_TIME} \
		--only-summary
}

load_testing_ui() {
	echo "Starting load testing UI"
	docker-ci locust -f utils/locustfile.py --host ${WEBSERVER_URL}
}


# Script starting point
if [[ -n $1 ]]; then
	set_common_env_variables
	case "$1" in
		tf_launch)
			printf "🚀  Run Terraform to launch new instance(s)...\n"
			tf_launch
			exit 0
			;;
		tf_provision)
			printf "👷‍♂️  Run Terraform+Ansible to git clone repo and start webapp on new instance(s)\n"
			tf_provision
			exit 0
			;;
		tf_destroy)
			printf "💥  Run Terraform to destroy instance(s) and created resource(s)...\n"
			tf_destroy
			exit 0
			;;
		cfn_create)
			printf "👷‍♂️  Run Cloudformation to create AWS infrastructure...\n"
			cfn_package
			cfn_create
			wait_for_stack_status "CREATE_IN_PROGRESS" "CREATE_COMPLETE"
			exit 0
			;;
		cfn_update)
			printf "🔃 	Run Cloudformation to update AWS infrastructure...\n"
			cfn_package
			cfn_update
			wait_for_stack_status "UPDATE_IN_PROGRESS" "UPDATE_COMPLETE"
			exit 0
			;;
		cfn_destroy)
			printf "💥  Run Cloudformation to destroy AWS infrastructure...\n"
			cfn_destroy
			wait_for_stack_status "DELETE_IN_PROGRESS" "DELETE_COMPLETE"
			exit 0
			;;
		cfn_destroy_async)
			printf "⏳  Run Cloudformation to destroy AWS infrastructure (async call)...\n"
			cfn_destroy
			exit 0
			;;
		code_deploy)
			printf "🚚 Run AWS CodeDeploy to deploy application to launched instances...\n"
			code_deploy_push
			code_deploy_create
			wait_for_codedeploy_status '"InProgress"' '"Succeeded"'
			exit 0
			;;
		load_testing)
			printf "📈 	Run load testing on deployed web application...\n"
			load_testing
			exit 0
			;;
		load_testing_ui)
			printf "📈  Start UI for load testing on deployed web application...\n"
			load_testing_ui
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
