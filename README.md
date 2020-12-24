Simplified version of https://github.com/gbourniq/portfolio


- simplify core app: Keep only Django, and remove celery worker, redis, nginx, postgres containers... these will be managed externally by AWS services such as SQS/SNS/RDS
- Removed Ansible / k8s stuff / docker-compose stuff (to be replaced by CloudFormation) and a single Dockerfile to be run by Make
- Simplified environment variables and scripts
- address all pylint warnings