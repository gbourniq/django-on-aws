#!/bin/bash

# Start application
# service httpd start

IMAGE_REPOSITORY=gbournique/django-on-aws
TAG=1.0.0

# Running app container, with AWS RDS Postgres as a DB backend
docker run -d \
    -p 80:8080 \
    --restart=no \
    --env POSTGRES_HOST=${RDS_POSTGRES_HOST} \
    --env POSTGRES_PASSWORD=${RDS_POSTGRES_PASSWORD} \
    ${IMAGE_REPOSITORY}:${TAG}