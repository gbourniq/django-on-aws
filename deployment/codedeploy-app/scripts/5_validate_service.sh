#!/bin/bash

# Source instance environment variables set in cfn-init
source /root/.bashrc

# Verify DB connection
[[ ! -z "${RDS_POSTGRES_HOST}" ]] || echo "RDS_POSTGRES_HOST not set"
[[ ! -z "${RDS_POSTGRES_PASSWORD}" ]] || echo "RDS_POSTGRES_PASSWORD not set"
psql -d "postgresql://postgres:${RDS_POSTGRES_PASSWORD}@${RDS_POSTGRES_HOST}/portfoliodb" -c "select now()"

# Verify Redis connection 
/redis-stable/src/redis-cli -c -h ${ELASTICACHE_REDIS_HOST} -p ${ELASTICACHE_REDIS_PORT} ping

# Verify we can access our webpage successfully
# curl -v --silent localhost:80 2>&1 | grep Congratulations



# Check running container health given a docker image name
# Usage: ./utils/healthcheck.sh "<IMAGE_REPOSITORY>" "<TAG>"

# trap "echo 'Something went wrong! Tidying up...' && exit 1" ERR

# # Helper functions
# function get_service_health() {
#   echo "$1" | xargs -I ID docker inspect -f '{{if .State.Running}}{{ .State.Health.Status }}{{end}}' ID
# }

# function check_service_health() {
#   container_id=$(docker ps --filter "ancestor=$1:$2" -qa)

#   # Check if container exists
#   if [[ -z "${container_id}" ]]; then
#     echo "❌ Container $1 is not running.. Aborting!"
#     exit 1
#   fi;

#   # Wait for the container to fully start up
#   until [[ $(get_service_health "${container_id}") != "starting" ]]; do
#     sleep 1
#   done;

#   # Check if container status shows healthy
#   if [[ $(get_service_health "${container_id}") != "healthy" ]]; then
#     echo "❌ $1 failed health check"
#     exit 1
#   fi;

#   echo "Container running from $1:$2 is healthy 🍀"
# }

# # Start script
# IMAGE_REPOSITORY=gbournique/django-on-aws
# TAG=1.0.0

# echo "Checking health for container running from $IMAGE_REPOSITORY:$TAG..."
# check_service_health "$IMAGE_REPOSITORY" "$TAG"
# echo "✅  All services are up and healthy!"
