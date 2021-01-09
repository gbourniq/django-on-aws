#!/usr/bin/env bash

set -e

# Variables: set with Environment Variable or revert to default value
AWS_DEFAULT_PROFILE="${AWS_DEFAULT_PROFILE:-myaws}"
STACK_NAME="${STACK_NAME:-myapp}"

# Delete the stack
echo "Deleting stack ${STACK_NAME}..."
aws cloudformation delete-stack --stack-name="${STACK_NAME}"

# Check Stack deletion status
function get_stack_status()
{
    if ! (aws cloudformation describe-stacks --stack-name=${STACK_NAME} >/dev/null 2>&1); then    
        # Stack with id ${STACK_NAME} does not exist.
        exit 0
    else
        STACK_STATUS=$(aws cloudformation describe-stacks --stack-name=${STACK_NAME} | jq -r '.Stacks[0].StackStatus')
        echo ${STACK_STATUS}
    fi
}

while [[ "$(get_stack_status)" == "DELETE_IN_PROGRESS" ]]; do
    echo "Stack deletion in progress 🧨"
    sleep 30
done

echo "Stack deleted successfully! ✅"