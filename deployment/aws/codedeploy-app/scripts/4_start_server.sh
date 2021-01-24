#!/bin/bash

set -x

# Source environment variables set from cfn-init
source /root/.bashrc

# should be in stop_server.sh only..
systemctl stop httpd.service

# Start application / TODO: remove hardcoded vars
IMAGE_REPOSITORY=gbournique/django-on-aws
TAG=1.0.0
docker pull ${IMAGE_REPOSITORY}:${TAG}
docker run -d \
    -p 80:8080 \
    --restart=no \
    --env POSTGRES_HOST=${RDS_POSTGRES_HOST} \
    --env POSTGRES_PASSWORD=${RDS_POSTGRES_PASSWORD} \
    --env STATICFILES_BUCKET=${S3_BUCKET_NAME_STATICFILES} \
    --env DEBUG=False \
    ${IMAGE_REPOSITORY}:${TAG}