#!/bin/bash
# Note the ApplicationStop lifecycle event runs the script from last successful revision
# because the lifecycle event is trying to stop the application revision installed last time
# To run the latest, cd /opt/codedeploy-agent/deployment-root && rm -rf *, sudo service codedeploy-agent restart
# All other lifecycle events run scripts from the current revision.
# Stop sample Apache server if it's running

set -x


isExistApp=$(pgrep httpd)
if [[ -n  $isExistApp ]]; then
    systemctl stop httpd.service
fi

IMAGE_REPOSITORY=gbournique/django-on-aws
TAG=1.0.0

# Stop and remove Django app container if it's running
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)