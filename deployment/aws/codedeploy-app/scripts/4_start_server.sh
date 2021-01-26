#!/bin/bash

set -x

# Variables - TODO: remove hardcoded vars
IMAGE_REPOSITORY=gbournique/django-on-aws
TAG=1.0.0

# Source environment variables set from cfn-init
source /root/.bashrc

# should be in stop_server.sh only.. TODO: try to get rid of it
systemctl stop httpd.service

# Start application
docker pull ${IMAGE_REPOSITORY}:${TAG}
docker run -d \
    -p 80:8080 \
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