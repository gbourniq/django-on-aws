# Makefile helpers


#### CloudFormation helpers ####
wait_for_stack_creation_status = { \
  until [[ "$$($(call get_stack_status))" != "CREATE_IN_PROGRESS" ]]; do sleep 5; done; \
  if [[ "$$($(call get_stack_status))" != "CREATE_COMPLETE" ]]; \
    then echo "Oops, something went wrong during stack creation ❌"; exit 1; \
  fi; \
  echo "Stack creation completed! ✅"; \
}

wait_for_stack_update_status = { \
  until [[ "$$($(call get_stack_status))" != "UPDATE_IN_PROGRESS" && "$$($(call get_stack_status))" != "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS" ]]; do sleep 5; done; \
  if [[ "$$($(call get_stack_status))" != "UPDATE_COMPLETE" ]]; \
    then echo "Oops, something went wrong during stack update ❌"; exit 1; \
  fi; \
  echo "Stack update completed! ✅"; \
}

wait_for_stack_delete_status = { \
  until [[ "$$($(call get_stack_status))" != "DELETE_IN_PROGRESS" ]]; do sleep 5; done; \
  echo "Stack delete completed! ✅"; \
}

get_stack_status = { \
	echo $$(aws cloudformation describe-stacks --stack-name=${STACK_NAME} | jq -r '.Stacks[0].StackStatus'); \
}

get_stack_output = { \
	echo $$(aws cloudformation describe-stacks \
		--stack-name ${STACK_NAME} \
		--query 'Stacks[].Outputs[?OutputKey==`$(1)`].OutputValue' \
		--output text); \
}

#### CodeDeploy helpers ####
define codedeploy_s3_artifact
echo $$(echo "bucket=$$($(call get_stack_output, CodeDeployS3BucketName)),\
key=$$($(call codedeploy_s3_key_name)),\
bundleType=zip,\
eTag=$$($(call codedeploy_s3_key_eTag)),\
version=$$($(call codedeploy_s3_key_version))" | sed 's/[[:space:]]*//g')
endef

codedeploy_s3_key_name = { echo "$$($(call get_codedeploy_revision_attribute, key))"; }
codedeploy_s3_key_eTag = { echo "$$($(call get_codedeploy_revision_attribute, eTag))"; }
codedeploy_s3_key_version = { echo "$$($(call get_codedeploy_revision_attribute, version))"; }

# Syntax: $(call get_codedeploy_revision_attribute,<s3LocationAttribute>)
get_codedeploy_revision_attribute = { \
	echo $$(aws deploy list-application-revisions \
				--application-name "$$($(call get_stack_output, CodeDeployApplicationName))" \
				--query "revisions[].s3Location[].$(1)" \
				--sort-by registerTime \
				--sort-order descending \
				--max-items 1 | jq '.[]' | sed 's/\"//g'); \
}

wait_for_codedeploy_deployment_status = { \
  until [[ "$$($(call get_deployment_status))" != '"InProgress"' ]]; \
    do sleep 1; \
  done; \
  if [[ "$$($(call get_deployment_status))" != '"Succeeded"' ]]; \
    then echo "Deployment failed"; exit 1; \
  fi; \
  echo "Deployment succeeded!"; \
}

get_deployment_status = { \
	echo $$(aws deploy get-deployment \
				--deployment-id $$($(call codedeploy_latest_deployment_id)) \
				--query "deploymentInfo.status"); \
}

codedeploy_latest_deployment_id = { \
	echo $$(aws deploy list-deployments \
				--application-name "$$($(call get_stack_output, CodeDeployApplicationName))" \
				--deployment-group-name "$$($(call get_stack_output, CodeDeployDeploymentGroupName))" \
				--query "deployments" \
				--max-items 1 | jq '.[]' | sed 's/\"//g'); \
}

# Cosmetics
RED := "\e[1;31m"
YELLOW := "\e[1;33m"
GREEN := "\033[32m"
NC := "\e[0m"
INFO := bash -c 'printf ${YELLOW}; echo "[INFO] $$1"; printf ${NC}' MESSAGE
MESSAGE := bash -c 'printf ${NC}; echo "$$1"; printf ${NC}' MESSAGE
SUCCESS := bash -c 'printf ${GREEN}; echo "[SUCCESS] $$1"; printf ${NC}' MESSAGE
WARNING := bash -c 'printf ${RED}; echo "[WARNING] $$1"; printf ${NC}' MESSAGEs