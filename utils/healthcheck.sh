#!/bin/bash
set -e

# Check running container health given a docker image name
# Usage: ./utils/healthcheck.sh "<IMAGE_REPOSITORY>" "<TAG>"

trap "echo 'Something went wrong! Tidying up...' && exit 1" ERR

# Helper functions
function get_service_health() {
  echo "$1" | xargs -I ID docker inspect -f '{{if .State.Running}}{{ .State.Health.Status }}{{end}}' ID
}

function check_service_health() {
  container_id=$(docker ps --filter "name=$1" -qa)

  # Check if container exists
  if [[ -z "${container_id}" ]]; then
    echo "❌ Container $1 is not running.. Aborting!"
    exit 1
  fi;

  # Wait for the container to fully start up
  until [[ $(get_service_health "${container_id}") != "starting" ]]; do
    sleep 1
  done;

  # Check if container status shows healthy
  if [[ $(get_service_health "${container_id}") != "healthy" ]]; then
    echo "❌ $1 failed health check"
    exit 1
  fi;

  echo "Container $1 running is healthy 🍀"
}

# Start script
echo "Checking health for $1 container"
check_service_health "$1"
echo "✅  All services are up and healthy!"
