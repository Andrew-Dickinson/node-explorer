# syntax=docker/dockerfile:1

FROM node:16-alpine

WORKDIR /app

COPY package*.json ./

RUN npm ci

ENV REACT_APP_COMMIT_HASH=$GIT_COMMIT_HASH

COPY . .

RUN npm run build
