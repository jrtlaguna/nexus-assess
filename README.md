![Coverage Status](coverage.svg)

# Nexus Criticality Assessment Backend

This repository is used for the backend of the Nexus Criticality Assessment Backend App developed using Django.

## Docker Setup

To run this project in a Docker it is assumed you have a setup [Docker Compose](https://docs.docker.com/compose/).

**Install Docker:**

- Linux - [get.docker.com](https://get.docker.com/)
- Windows or MacOS - [Docker Desktop](https://www.docker.com/products/docker-desktop)

1. Open CLI and CD to project root.
2. Clone this repo and `git clone git@github.com:jrtlaguna/nexus-assess-backend.git`
3. Go to project folder where manage.py is located.
4. Execute `docker-compose up --build` This will build the docker container.
5. `docker exec -it nexus_assess_backend_web python manage.py migrate`
6. `docker exec -it nexus_assess_backend_web python manage.py createsuperuser`

### Docker Notes:

You will only execute `docker-compose up --build` if you have changes in your Dockerfile. To start docker containers you can either use `docker-compose up` or `docker-compose start`

**Docker Django Environments**

1. To add or use different environment values copy `docker-compose.override.yml.example` and rename it to `docker-compose.override.yml`
   and change or add environment variables needed.
2. Add a `.env` file in your project root.

Any changes in the environment variable will need to re-execute the `docker-compose up`

**Docker Specific .env configuration**

1. Postgres - Postgres server will be running on the system host not in a docker container, so you should use `host.docker.internal` when setting the database url. Example, `DATABASE_URL=postgres://user:password@host.docker.internal/nexus_assess_backend`
2. Redis - Redis will be running on a separate container, so adjust the hostname accordingly. Example,
   `CELERY_BROKER_URL=redis://redis:6379/0`

**To add package to poetry**

```sh
docker exec -it nexus_assess_backend_web poetry config virtualenvs.create false
docker exec -it nexus_assess_backend_web poetry add new_package_name
```

**Example of executing Django manage.py commands**

```sh
docker exec -it nexus_assess_backend_web python manage.py shell
docker exec -it nexus_assess_backend_web python manage.py makemigrations
docker exec -it nexus_assess_backend_web python manage.py loaddata appname
```

**To copy site-packages installed by poetry from docker to your host machine**

```sh
docker cp nexus_assess_backend_web:/usr/local/lib/python3.11.5/site-packages <path where you want to store the copy>
```

**DEBUG NOTES:**

1. When adding PDB to your code you can interact with it in your CLI by executing `docker start -i nexus_assess_backend_web`.
2. If you experience this error in web docker container `port 5432 failed: FATAL:  the database system is starting up` -- automatically force restart the nexus_assess_backend_web docker container by executing.

```sh
docker restart nexus_assess_backend_web
```

## Local Environment Setup

### Required Installations

1. [Python 3.11.5](https://www.python.org/downloads/)
   On macOS (with Homebrew): `brew install python3`
2. [Poetry 1.1.11](https://python-poetry.org/docs/#installation)
   `curl -sSL https://install.python-poetry.org | python3 -`
3. [PostgreSQL 14.0](https://www.postgresql.org/download/)
   On macOS (with Homebrew): `brew install postgres`

### Install Requirements

1. `poetry install`
   This installs the libraries required for this project
2. `pre-commit install`
   This installs pre-commit hooks to enforce code style.

### Setup PostgreSQL Database

```bash
sudo -u postgres psql

CREATE USER nexus_assess_backend WITH PASSWORD 'nexus_assess_backend';
ALTER USER nexus_assess_backend CREATEDB;

CREATE DATABASE nexus_assess_backend owner nexus_assess_backend;
```

### Configure .env File

1. Copy `.env.example` to `.env` and customize its values.
2. `SECRET_KEY` should be a random string, you can generate a new one using the following command:
   `python -c 'from secrets import token_urlsafe; print("SECRET_KEY=" + token_urlsafe(50))'`
3. Set `DATABASE_URL` to `POSTGRES_URL=postgres://nexus_assess_backend:nexus_assess_backend@localhost/nexus_assess_backend`.

### Setup DB Schema

1. `./manage.py migrate`
   This applies the migrations to your database
2. `./manage.py createsuperuser`
   This creates your superuser account. Just follow the prompts.

## Running the App

1. `poetry shell`
   If it's activated you'll see the virtual environment name at the beginning of your prompt, something like `("nexus_assess_backend"-2wVcCnjv-py3.11.5)`.
2. `./manage.py runserver`

## Running the Celery Server

1. Make sure you have a Redis server running on localhost with the default port (6379). More information on how to setup [here](https://redis.io/docs/getting-started/installation/install-redis-on-mac-os/)
2. Set the `CELERY_BROKER_URL` env var to `redis://localhost:6379/0`
3. `celery -A nexus_assess_backend worker -l info`
   This starts a Celery worker that will process the background tasks.
4. `celery -A nexus_assess_backend beat -l info`
   This starts the Celery beat scheduler that will trigger the periodic tasks.

## Running the Tests

1. `poetry shell`
2. `pytest`
   Run `pytest --cov=. --cov-report term-missing` to also show coverage report.
   Run `pytest --cov=. --cov-report=html` to generate html report

# FAQs

1. Changing the `.env` file variables has no effect.
   Run `export $(grep -v '^#' .env | xargs -0)` to source the file
   or
   Exit shell and run `poetry shell` again to reload the env file

## Additional Deployment Commands

1. python manage.py import_source_table
2. python manage.py loaddata requirements/fixtures/compliance.json
