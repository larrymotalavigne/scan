### STAGE 1: Base ###
FROM node:24-alpine AS base
WORKDIR /usr/src/app
COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps
COPY . .
RUN npm run build:prod

### STAGE 2: Run ###
FROM nginx:latest
RUN apt-get update && apt-get -y upgrade
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=base /usr/src/app/dist /usr/share/nginx/html
