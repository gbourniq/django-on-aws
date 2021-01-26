#!/bin/bash

set -x

# Note the ApplicationStop lifecycle event runs the script from last successful revision
# (All other lifecycle events run scripts from the current revision.)
# To run the latest revision anyway, run: cd /opt/codedeploy-agent/deployment-root && rm -rf *, sudo service codedeploy-agent restart

# Stop the sample Apache server if it's running
isExistApp=$(pgrep httpd)
if [[ -n  $isExistApp ]]; then
    systemctl stop httpd.service
fi

# Clean up any existing containers
docker stop $(docker ps -a -q) || true
docker rm $(docker ps -a -q) || true