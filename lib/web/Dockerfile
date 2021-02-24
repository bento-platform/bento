ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

USER root

RUN apk update
RUN apk add git nginx
RUN apk upgrade

COPY nginx.conf /etc/nginx/conf.d/nginx.conf

RUN mkdir /web
WORKDIR /web

ARG BENTO_WEB_REPO
ARG BENTO_WEB_BRANCH


RUN git clone "${BENTO_WEB_REPO}"
WORKDIR /web/bento_web
RUN git fetch && \
    git checkout "${BENTO_WEB_BRANCH}" && \
    git pull

RUN rm -rf package-lock.json npm-shrinkwrap.json node_modules && \
    npm cache clean --force && \
    npm cache verify && \
    npm install && \
    npm run build-dev

# fix crash at runtime
RUN mkdir /run/nginx && \
    touch /run/nginx/nginx.pid 
#\ && chown -R api-gatway:api-gatway /run/nginx.pid /cache/nginx

# Run
CMD ["nginx", "-g", "daemon off;"]
