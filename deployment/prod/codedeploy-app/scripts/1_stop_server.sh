#!/bin/bash
set -e
# Gracefully stop the application or remove currently installed packages in preparation for a deployment.
# Note the ApplicationStop lifecycle event runs the script from last successful revision,
# while all other lifecycle events run scripts from the current revision.

echo "Clean up any running containers"
docker stop $(docker ps -a -q) || true
docker rm $(docker ps -a -q) || true