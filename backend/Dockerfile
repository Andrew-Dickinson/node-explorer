# syntax=docker/dockerfile:1

FROM node-explorer-frontend AS frontend
FROM tiangolo/uwsgi-nginx-flask:python3.11

WORKDIR /app

COPY . .
RUN pip3 install .

COPY --from=frontend /app/build static/