# Note regarding python-alpine:
# https://dev.to/pmutua/the-best-docker-base-image-for-your-python-application-3o83
FROM python:3.11.5-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /web

RUN pip install poetry

COPY . /web

RUN POETRY_VIRTUALENVS_CREATE=false poetry install

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "nexus_assess_backend.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--reload"]
