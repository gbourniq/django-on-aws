#!/bin/bash

set -x

EC2_INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
EC2_AZ=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)

# Assume /var/www/html/index.html was created at the Install Hook
# sed -i "s/was deployed/was deployed to deployment group $DEPLOYMENT_GROUP_NAME on $(hostname -f) ($EC2_INSTANCE_ID) in $EC2_AZ/g" /var/www/html/index.html