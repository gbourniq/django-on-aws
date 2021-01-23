#!/bin/bash

# Source instance environment variables set in cfn-init
source /root/.bashrc

# Verify DB connection
psql -d "postgresql://postgres:${RDS_POSTGRES_PASSWORD}@${RDS_POSTGRES_HOST}/portfoliodb" -c "select now()"

# Verify Redis connection 
/redis-stable/src/redis-cli -c -h ${ELASTICACHE_REDIS_HOST} -p ${ELASTICACHE_REDIS_PORT} ping

# Verify we can access our webpage successfully
curl -v --silent localhost:80 2>&1 | grep Congratulations