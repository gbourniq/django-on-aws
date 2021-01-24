#!/bin/bash

set -x

# Start application
# service httpd start

IMAGE_REPOSITORY=gbournique/django-on-aws
TAG=1.0.0

# should be in stop_server.sh only..
systemctl stop httpd.service

source /root/.bashrc

# ${S3_BUCKET_NAME_STATICFILES}
# Running app container, with AWS RDS Postgres as a DB backend
docker pull ${IMAGE_REPOSITORY}:${TAG}
docker run -d \
    -p 80:8080 \
    --restart=no \
    --env POSTGRES_HOST=${RDS_POSTGRES_HOST} \
    --env POSTGRES_PASSWORD=${RDS_POSTGRES_PASSWORD} \
    --env STATICFILES_BUCKET=prod.bournique.fr-static-files \
    --env DEBUG=False \
    ${IMAGE_REPOSITORY}:${TAG}