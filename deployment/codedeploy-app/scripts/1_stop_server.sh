#!/bin/bash

# Stop sample Apache server if it's running
isExistApp=$(pgrep httpd)
if [[ -n  $isExistApp ]]; then
    service httpd stop        
fi

IMAGE_REPOSITORY=gbournique/django-on-aws
TAG=1.0.0

# Stop and remove Django app container if it's running
docker rm --force $(docker ps --filter "ancestor=${IMAGE_REPOSITORY}:${TAG}" -qa) || true