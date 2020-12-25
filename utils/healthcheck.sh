#!/bin/bash
set -e

trap "echo 'Something went wrong! Tidying up...' && exit 1" ERR


# Helper functions

function get_service_health() {
  echo "$1" | xargs -I ID docker inspect -f '{{if .State.Running}}{{ .State.Health.Status }}{{end}}' ID
}

function check_service_health() {

  container_id=$(docker ps -aqf "name=$1")

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

  echo "$1 healthy 🍀"
}

# Start script
echo "Checking services health..."
services=(postgres app)
for service in ${services[*]}; do
    check_service_health "$service"
done
echo "✅ All services are up and healthy!"
