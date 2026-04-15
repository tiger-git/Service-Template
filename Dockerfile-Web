# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/


ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION} as base


RUN pip install --upgrade pip && pip install --no-cache-dir poetry

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml ./

RUN poetry install --no-root

COPY . .

EXPOSE 8521

CMD poetry run uvicorn 'main:app' --host=0.0.0.0

