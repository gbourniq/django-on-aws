#!/bin/bash

set -x

# Variables - TODO: remove hardcoded vars
IMAGE_REPOSITORY=gbournique/django-on-aws
TAG=1.0.0
CONTAINER_NAME=myapp

# Source environment variables set from cfn-init
source /root/.bashrc

# should be in stop_server.sh only.. TODO: try to get rid of it
systemctl stop httpd.service

# Start application
docker pull ${IMAGE_REPOSITORY}:${TAG}
docker run -d \
    -p 80:8080 \
    --name=${CONTAINER_NAME} \
    --restart=no \
    --log-driver=awslogs \
    --log-opt awslogs-group=${DOCKER_LOGS_LOG_GROUP_NAME} \
    --mount type=bind,source=/home/ec2-user/mounts/startup_server.sh,target=/home/portfoliouser/mounts/ \
    --mount type=volume,source=app-logs,target=/home/portfoliouser/app/logs/ \
    --env POSTGRES_HOST=${RDS_POSTGRES_HOST} \
    --env POSTGRES_PASSWORD=${RDS_POSTGRES_PASSWORD} \
    --env STATICFILES_BUCKET=${STATICFILES_BUCKET} \
    --env AWS_S3_CUSTOM_DOMAIN=${WEBAPP_DOMAIN} \
    --env DEBUG=True \
    ${IMAGE_REPOSITORY}:${TAG}

# Write some instance details to the footer.html file
EC2_INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
EC2_AZ=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
HTML_PAGE=/home/portfoliouser/app/main/templates/main/includes/footer.html
docker exec $CONTAINER_NAME sed -i "s/aws-ec2-details-placeholder/Running on AWS | $(hostname -f) | $EC2_INSTANCE_ID | $EC2_AZ/g" $HTML_PAGE