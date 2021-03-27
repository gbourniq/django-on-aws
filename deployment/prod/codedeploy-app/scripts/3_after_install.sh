#!/bin/bash
set -e
# Define tasks after the install hook (after CodeDeploy agent copied files to the host),
# such as configuring your application or changing file permissions.

sudo chmod +x /home/ec2-user/mounts/startup_server.sh