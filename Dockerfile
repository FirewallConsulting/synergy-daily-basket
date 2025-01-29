# syntax=docker/dockerfile:1
FROM python:3.11-alpine

RUN addgroup -S sdb && adduser -S celeryuser -G sdb

WORKDIR /docker-sdb

RUN apk add --no-cache gcc musl-dev linux-headers

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY . .
