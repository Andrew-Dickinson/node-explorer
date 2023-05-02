# syntax=docker/dockerfile:1

FROM node-explorer-frontend AS frontend
FROM tiangolo/uwsgi-nginx-flask:python3.11

WORKDIR /app

# Copy the pyproject.toml file into the container
COPY pyproject.toml ./

# Install dependencies
RUN pip3 install setuptools wheel && \
    pip3 install --no-cache-dir .

COPY . .
RUN pip3 install .

COPY --from=frontend /app/build static/

ENV FLASK_ENV=production