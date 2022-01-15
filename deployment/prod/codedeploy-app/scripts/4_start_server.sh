#!/bin/bash
set -ex
# Script to restart services that were stopped during ApplicationStop

# Source environment variables set from cfn-init
source /root/.bashrc

# Stop the sample Apache server if it's running
# Stopping here because the ApplicationStop lifecycle hook
# is never run on a new instance from a scale out event
systemctl stop httpd.service || true


echo "Get the image name and debug bool from the SSM Parameter service"
IMAGE_NAME=$(aws ssm get-parameter \
                --name "/CODEDEPLOY/DOCKER_IMAGE_NAME" \
                --query "Parameter.Value" \
                --output text \
                --region "${AWS_REGION}")
DEBUG=$(aws ssm get-parameter \
                --name "/CODEDEPLOY/DEBUG_DEMO" \
                --query "Parameter.Value" \
                --output text \
                --region "${AWS_REGION}")          
CONTAINER_NAME=myapp

echo "Pulling and running docker container for ${IMAGE_NAME}"
docker pull ${IMAGE_NAME}

echo 'Create app-logs volume and change permissions to non-root user'
docker volume create app-logs
chown -R 1000:1000 /var/lib/docker/volumes/

echo 'Start webapp container'
docker run -d \
    -p 80:8080 \
    --name=${CONTAINER_NAME} \
    --restart=no \
    --log-driver=awslogs \
    --log-opt awslogs-group=${DOCKER_LOGS_LOG_GROUP_NAME} \
    --mount type=bind,source=/home/ec2-user/mounts/startup_server.sh,target=/home/portfoliouser/mounts/ \
    --mount type=volume,source=app-logs,target=/home/portfoliouser/app/logs/ \
    --env POSTGRES_HOST=${RDS_POSTGRES_HOST} \
    --env POSTGRES_PASSWORD=${RDS_POSTGRES_PASSWORD} \
    --env REDIS_ENDPOINT=${ELASTICACHE_REDIS_HOST}:${ELASTICACHE_REDIS_PORT} \
    --env STATICFILES_BUCKET=${STATICFILES_BUCKET} \
    --env AWS_S3_CUSTOM_DOMAIN=${WEBAPP_DOMAIN} \
    --env SNS_TOPIC_ARN=${DJANGO_APP_SNS_TOPIC_ARN} \
    --env SES_IDENTITY_ARN=${DJANGO_APP_SES_IDENTITY_ARN} \
    --env DEBUG=${DEBUG} \
    ${IMAGE_NAME}

echo "Write instance details to the footer.html file"
EC2_INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
EC2_AZ=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
HTML_PAGE=/home/portfoliouser/app/main/templates/main/includes/footer.html
sudo docker exec $CONTAINER_NAME sed -i "s/aws-ec2-details-placeholder/Running on AWS | $(hostname -f) | $EC2_INSTANCE_ID | $EC2_AZ/g" $HTML_PAGE