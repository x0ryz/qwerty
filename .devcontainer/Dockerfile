FROM mcr.microsoft.com/devcontainers/python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y \
        postgresql-client \
        build-essential \
        libpq-dev \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libjpeg-dev \
        libopenjp2-7-dev \
        libffi-dev \
        shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app/qwerty