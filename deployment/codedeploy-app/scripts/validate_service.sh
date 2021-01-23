#!/bin/bash

# Verify we can access our webpage successfully
curl -v --silent localhost:80 2>&1 | grep Congratulations

# Variables
# RDS_POSTGRES_HOST and REDIS_HOST can be retrieved from DatabaseStack.Outputs
AWS_REGION=eu-west-2
RDS_POSTGRES_HOST=ddmlr8z8nwfag2.cwr5v77jgf3a.eu-west-2.rds.amazonaws.com
RDS_PWD_SSM_SECURE_STRING_NAME=/RDS/POSTGRES_PASSWORD/SECURE
REDIS_HOST=dev-el-1awkk0kx3ce92.qg0t6p.0001.euw2.cache.amazonaws.com
REDIS_PORT=6379

# Verify DB connection
RDS_POSTGRES_PASSWORD=$(aws ssm get-parameter \
                            --name ${RDS_PWD_SSM_SECURE_STRING_NAME} \
                            --with-decryption \
                            --query "Parameter.Value" \
                            --output text \
                            --region ${AWS_REGION})
psql -d "postgresql://postgres:${RDS_POSTGRES_PASSWORD}@${RDS_POSTGRES_HOST}/portfoliodb" -c "select now()" > /dev/null

# Verify Redis connection 
/redis-stable/src/redis-cli -c -h ${REDIS_HOST} -p ${REDIS_PORT} ping