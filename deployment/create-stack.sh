#!/usr/bin/env bash
set -e

# Variables: set with Environment Variable or revert to default value
AWS_DEFAULT_PROFILE="${AWS_DEFAULT_PROFILE:-myaws}"
STACK_NAME="${STACK_NAME:-app}"
SNS_ARN="arn:aws:sns:eu-west-2:164045463835:CloudFormationNotifications"

# Stack tags
NAME="Guillaume Bournique"
EMAIL="gbournique.dev1@gmail.com"
LAUNCH_DATE="$(date +%F_%T)"

# File paths
DEPLOYMENT_DIR="${DEPLOYMENT_DIR:-$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )}"
CFN_TEMPLATE_FILE="${CFN_TEMPLATE_FILE:-$DEPLOYMENT_DIR/cfn-template-app.yaml}"
CFN_PARAMETERS_FILE="${CFN_PARAMETERS_FILE:-$DEPLOYMENT_DIR/cfn-template-parameters.json}"

# Helper functions
function exit_error() {
  echo "$1" 1>&2
  exit 1
}

function get_stack_status()
{
    STACK_STATUS=$(aws cloudformation describe-stacks --stack-name=${STACK_NAME} | jq -r '.Stacks[0].StackStatus')
    echo ${STACK_STATUS}
}

# Check if all required commands are available locally
available_commands=0;
REQUIRED_COMMANDS=(aws jq);
for command in "${REQUIRED_COMMANDS[@]}"; do
  if ! (hash "$command" &>/dev/null); then
    echo "$command is not available!"
    echo "Please run 'pip install $command'"
    exit 1
  fi
done

# Create the stack
echo "Creating stack ${STACK_NAME}..."
aws cloudformation create-stack \
    --stack-name=${STACK_NAME} \
    --template-body=file://"${CFN_TEMPLATE_FILE}" \
    --parameters=file://"${CFN_PARAMETERS_FILE}" \
    --tags "Key"="Name","Value"="${NAME}" "Key"="Date","Value"="${LAUNCH_DATE}" "Key"="Email","Value"="${EMAIL}" \
    --profile=${AWS_DEFAULT_PROFILE} \
    --notification-arns=${SNS_ARN} \
    --capabilities=CAPABILITY_NAMED_IAM

# Check Stack creation status
while [[ "$(get_stack_status)" == "CREATE_IN_PROGRESS" ]]; do
    echo "Stack creation in progress 🚀"
    sleep 30
done

if [[ "$(get_stack_status)" == "CREATE_COMPLETE" ]]; then
    echo "Stack creation completed! ✅"
    aws cloudformation describe-stacks --stack-name ${STACK_NAME} --query 'Stacks[].Outputs[].OutputValue' --output table
else
    exit_error "Oops, something went wrong during stack creation ❌"
fi