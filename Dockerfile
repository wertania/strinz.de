# Builds the whole thing from source and serves the result with nginx.
# Nothing runs at request time: the image contains static files only.
FROM node:22-alpine AS build
RUN apk add --no-cache python3
WORKDIR /app

COPY site/package.json site/package-lock.json* ./site/
RUN cd site && (npm ci || npm install)

COPY tools ./tools
COPY assets ./assets
COPY site ./site

RUN python3 tools/pipeline.py \
 && cd site \
 && npm run images \
 && npx astro build

FROM nginx:1.27-alpine
COPY site/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/site/dist /usr/share/nginx/html
EXPOSE 80
