"""
Lambda function to push custom metrics, FAILURE or SUCCESS,
based on CodeDeploy deployment state change notification
"""
import datetime
from os import getenv

import boto3


# pylint: disable=unused-argument
def handler(event, context):
    """Lambda function to push custom metrics, FAILURE or SUCCESS,
    based on CodeDeploy deployment state change notification"""
    try:
        # Retrieve environment variables
        dimension_name = getenv("CODEDEPLOY_DIMENSION_NAME")
        metric_name = getenv("CODEDEPLOY_METRIC_NAME")
        if not dimension_name or not metric_name:
            return "CODEDEPLOY_DIMENSION_NAME or CODEDEPLOY_METRIC_NAME not set"

        # Get deployment state from CodeDeploy event
        deployment_state = event["detail"]["state"]
        print(f"Deployment state: {deployment_state}")

        # Pushing custom metric to CW
        response = boto3.client("cloudwatch").put_metric_data(
            MetricData=[
                {
                    "MetricName": metric_name,
                    "Dimensions": [{"Name": dimension_name, "Value": deployment_state}],
                    "Unit": "None",
                    "Value": 1,
                    "Timestamp": datetime.datetime.now(),
                },
            ],
            Namespace="CodeDeployDeploymentStates",
        )
        print(f"Response from CW service: {response}")
        return response
    # pylint: disable=broad-except
    except Exception as excpt:
        print(f"Execution failed... {excpt}")
        return None
