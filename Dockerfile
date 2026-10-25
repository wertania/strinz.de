# Builds the whole thing from source and serves the result with nginx.
# Nothing runs at request time: the image contains static files only.
FROM node:24-alpine AS build
RUN apk add --no-cache python3
WORKDIR /app

COPY site/package.json site/package-lock.json* ./site/
RUN cd site && npm ci

COPY tools ./tools
COPY assets ./assets
COPY site ./site

RUN python3 tools/pipeline.py \
 && cd site \
 && npm run images \
 && npx astro build

FROM nginx:stable-alpine
COPY site/nginx.conf /etc/nginx/conf.d/default.conf
COPY site/security-headers.conf /etc/nginx/security-headers.conf
COPY --from=build /app/site/dist /usr/share/nginx/html
EXPOSE 80
