# syntax=docker/dockerfile:1

FROM node:16-alpine

WORKDIR /app

COPY . .
RUN npm ci
RUN npm run build
