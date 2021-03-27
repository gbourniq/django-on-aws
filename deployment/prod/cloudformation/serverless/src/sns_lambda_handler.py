import json
from os import getenv

import urllib3

http = urllib3.PoolManager()


def handler(event, context):
    """Lambda function to forward SNS notifications to Slack"""
    try:
        # Initialize variables
        url = getenv("SLACK_WEBHOOK_URL")
        text = event["Records"][0]["Sns"]["Message"]

        # Check slack configuration
        if not url:
            print(f"Invalid slack configuration. SNS message: {text}")
            return
        # Post SNS message to Slack
        msg = {
            "channel": "#general",
            "username": "SNS",
            "text": text,
            "icon_emoji": ":cloud:",
        }
        encoded_msg = json.dumps(msg).encode("utf-8")
        resp = http.request("POST", url, body=encoded_msg)
        print({"message": text, "status_code": resp.status, "response": resp.data})

    except Exception as excpt:
        print(f"Execution failed... {excpt}")
