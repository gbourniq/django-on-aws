[![Build Status](https://travis-ci.com/gbourniq/django-on-aws.svg?branch=main)](https://travis-ci.com/gbourniq/django-on-aws)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
![Pylint](.github/app.svg)
![Coverage](.github/coverage.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/gbourniq/django-on-aws/blob/master/LICENSE)

## Overview
This repository is a simplified version of https://github.com/gbourniq/portfolio, which previously involved a monolithic application defined by multiple containers deployed on a single server. This new repository attempts to implement a microservices approach by using AWS managed services, which will improve performance and maintainability.
- `Nginx` -> `AWS Load Balancer` with SSL certificate
- `Django server` -> `AWS ECS` (previously as docker container on EC2)
- `Redis` -> `AWS ElastiCache` / `AWS DynamoDB`
- `Celery` worker -> `AWS Lambda` & `SQS Queues`
- `Postgres` -> `AWS RDS`

Other key differences compared to the previous version are:
- Keep docker-compose to only spin up Django server and postgres containers for local testing (removed all other services)
- Simplied environment variables and removed all bash scripts
- Removed Ansible / Kubernetes files - Deployment will be managed with CloudFormation
- Address all pylint warnings, improve test coverage and general code improvements

## Contents
- [Prerequisites](#prerequisites)
- [Virtual environment and git-hooks setup](#virtual-environment-and-git-hooks-setup)
- [Local development and testing](#local-development-and-testing)
- [Build and push docker image](#build-and-push-docker-image)
- [Configure RDS Postgres as a database backend](#configure-rds-postgres-as-a-database-backend)
- [Deployment to AWS](#deployment-to-aws)
- [CI/CD](#cicd)
- [RESTful APIs (WIP)](#restful-apis-wip)

## Prerequisites
- Install [Docker](https://hub.docker.com/search/?type=edition&offering=community)
- Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) 
- Install [Poetry](https://github.com/sdispater/poetry)
- Install [Make](https://www.gnu.org/software/make/)

## Virtual environment and git-hooks setup

To make things easy, you can create the conda environment and install the dependencies by running:
```bash
make env
conda activate django-on-aws
```
> Note: the environment can then be updated using the `make env-udpate` command when poetry packages are modified.

A [pre-commit](https://pypi.org/project/pre-commit/) package is used to manage git-hooks. The hooks are defined in `.pre-commit-config.yaml`, and will automatically format the code with `autoflake`, `isort` and `black`, and run code analysis and testing with `pylint` and `pytest`, on each commit. To set them up, run:
```bash
make pre-commit
```

Make sure to run `source .env` to avoid import errors


## Local development and testing

When running for the first time, please follow these steps:

1. Run postgres docker container with `make rundb`. This will automatically create a table as defined in `deployment/postgres/docker-entrypoint-initdb.d/run_db_setup.sh`. Note the table can be easily wiped with the `make recreatedb` command.

2. Create the django superuser required to access the `/admin` page:
```bash
python manage.py createsuperuser
```

3. Apply Django model migrations:
```bash
python manage.py makemigrations
python manage.py makemigrations main
python manage.py migrate
```

Once the above is set up, the local Django server can be quickly run with the following make command:
```bash
make runserver
```
> Note the above command will automatically starts a postgres container if it's not already up

Unit-tests and integration tests are run with `pytest-django` to cover the following:
* Simulate requests and insert test data from HTTP-level request handling
* Form validation and processing
* Template rendering
They can be run with the following make command:
```bash
make tests
```
> Note the above command will automatically starts a postgres container if it's not already up
> To view the unit-tests coverage report, run `make open-cov-report`

## Build and push docker image

Build the image with
```bash
make image
```

Start a container from the image along with a Postgres container
```bash
make up
```

Check app container health to ensure deployment configurations are correct
```bash
make healthcheck
```

Remove application and postgres container
```
make down
```

Push the docker image to dockerhub (the `DOCKER_PASSWORD` environment variable must be set)
```bash
make publish
```

## Run the application with RDS Postgres as a database backend

1. Launch an RDS database from the AWS console, and note the following values:
```
POSTGRES_HOST
POSTGRES_DB
POSTGRES_PORT
POSTGRES_PORT
POSTGRES_PASSWORD
```

2. Create a Table using Postgres management tools such as `pgadmin` or `SQLElectron`:
```bash
CREATE USER portfoliodb PASSWORD 'portfoliodb';
CREATE DATABASE portfoliodb;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO portfoliodb;
ALTER ROLE portfoliodb IN DATABASE portfoliodb SET search_path = portfoliodb,public;
```

3. Ensure the variables in step 1 are defined as environment variables and run the application docker container, either locally with `make run-app`, or from any server (eg. EC2 instance) with 
```bash
docker run -d \
	-p 8080:8080 \
	--name=myapp \
	--restart=no \
	--env POSTGRES_HOST=${POSTGRES_HOST} \
	--env POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
	${IMAGE_REPOSITORY}:$(TAG)
```

## Deployment to AWS

Not tested yet, though it should be as simple as running 
```bash
docker run -d \
	-p 8080:8080 \
	--name=myapp \
	--restart=always \
	--env POSTGRES_HOST=<rds-db-hostname> \
	--env POSTGRES_PASSWORD=<rds-db-password> \
	gbournique/django-on-aws:1.0.0
```

## CI/CD

The `.travis.yml` build configuration file defines the following CI/CD pipeline:

* Continuous Integration
```
make env                          <-- Create conda environment and install dependencies
conda activate django-on-aws      <-- Activate conda environment
make tests                        <-- Run unit-tests against the built-in FastAPI Testing server
```

* Continuous Deployment
```
make image                        <-- Build django application as a docker image
make up                           <-- Run a local postgres and app containers from the build image and a
make healthcheck                  <-- Check app container health
make down                         <-- Remove postgres and app containers
make publish                      <-- Push docker image to dockerhub
```

Note that the following secret environment variables must be set in the Travis Repository settings, so that the Travis server can push the docker image
```bash
DOCKER_PASSWORD
```

## RESTful APIs (WIP)

Web APIs have been developed using the [Django REST framework](https://www.django-rest-framework.org).

* Browse Category and Item model objects (`ListAPIView`):
```
api/v1/categories/
api/v1/categories/<id>/stats
api/v1/items/
```

* Add new Category and Item model objects (`CreateAPIView`) :
```
api/v1/categories/new
api/v1/items/new
```

* Edit and delete existing Category and Item model objects (`RetrieveUpdateDestroyAPIView`):
```
api/v1/categories/<id>/
api/v1/items/<id>/
```
> Note: Adding and editing objects requires to be logged in.
