#!/bin/bash

# Check DB connection (RDS_POSTGRES_HOST can retrieved after cfn creation)
RDS_POSTGRES_HOST=mpi1wm5ytapo4n.cwr5v77jgf3a.eu-west-2.rds.amazonaws.com
RDS_POSTGRES_PASSWORD=$(aws ssm get-parameter \
                            --name /RDS/POSTGRES_PASSWORD/SECURE \
                            --with-decryption \
                            --query "Parameter.Value" \
                            --output text \
                            --region ${AWS::Region})
psql -d "postgresql://postgres:${RDS_POSTGRES_PASSWORD}@${RDS_POSTGRES_HOST}/portfoliodb" -c "select now()" > /dev/null

# Check Redis Cache connection (REDIS_HOST can retrieved after cfn creation)
REDIS_HOST=mya-el-1t9fgr07ignse.qg0t6p.0001.euw2.cache.amazonaws.com
REDIS_PORT=6379
/redis-stable/src/redis-cli -c -h ${REDIS_HOST} -p ${REDIS_PORT} ping

# Start application
service httpd start

