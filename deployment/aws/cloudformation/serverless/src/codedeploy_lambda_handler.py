def handler(event, context):
    """Lambda function to push custom metrics, FAILURE or SUCCESS,
    based on CodeDeploy deployment state change notification"""
    try:
        # Get deployment state from CodeDeploy event
        deployment_state = event['detail']['state']
        print(f"Deployment state: {deployment_state}")
        return deployment_state
    except Exception as excpt:
        print(f"Execution failed... {excpt}")
        return None
