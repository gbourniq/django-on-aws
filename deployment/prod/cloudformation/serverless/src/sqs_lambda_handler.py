import json
from os import getenv

import urllib3

http = urllib3.PoolManager()


def handler(event, context):
    """Lambda function to forward SQS messages to Slack"""
    try:
        # Initialize variables
        url = getenv("SLACK_WEBHOOK_URL")
        sqs_messages = []
        for record in event["Records"]:
            payload = record["body"]
            print(f"SQS paylod: {payload}")
            sqs_messages.append(payload)

        # Check slack configuration
        if not url:
            print(f"Invalid slack configuration. SQS message: {sqs_messages}")
            return

        # Post up to 10 SQS record(s) to Slack
        msg = {
            "channel": "#general",
            "username": "SQS",
            "text": str(sqs_messages),
            "icon_emoji": ":cloud:",
        }
        encoded_msg = json.dumps(msg).encode("utf-8")
        resp = http.request("POST", url, body=encoded_msg)
        print(
            {"message": sqs_messages, "status_code": resp.status, "response": resp.data}
        )

    except Exception as excpt:
        print(f"Execution failed... {excpt}")
