[![Build Status](https://travis-ci.com/gbourniq/django-on-aws.svg?branch=main)](https://travis-ci.com/gbourniq/django-on-aws)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
![Pylint](.github/sam.svg)
![Coverage](.github/coverage.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/gbourniq/django-on-aws/blob/master/LICENSE)


Simplified version of https://github.com/gbourniq/portfolio


- simplify core app: Keep only Django, and remove celery worker, redis, nginx, postgres containers... these will be managed externally by AWS services such as SQS+Lambda/SNS/RDS/ElastiCache - view old docker_settings.py
- Removed Ansible / k8s stuff / docker-compose stuff (to be replaced by CloudFormation) and a single Dockerfile to be run by Make
- Simplified environment variables and scripts
- address all pylint warnings