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


ARG BENTO_WEB_IS_DEBUG
RUN mkdir bento_web/

RUN if [ "$BENTO_WEB_IS_DEBUG" = "true" ] ; then \
    echo "Building Web in Development Mode" ; \
    \
    else \
    git clone "${BENTO_WEB_REPO}" && \
    \
    cd ./bento_web && \
    \
    git fetch && \
    git checkout "${BENTO_WEB_BRANCH}" && \
    git pull ; \
    fi

RUN ls -la

# Copy startup scripts
COPY ./dev_startup.sh /web/dev_startup.sh
COPY ./startup.sh /web/startup.sh

WORKDIR /web/bento_web


# fix crash at runtime
RUN mkdir /run/nginx && \
    touch /run/nginx/nginx.pid 
#\ && chown -R api-gatway:api-gatway /run/nginx.pid /cache/nginx
RUN npm config set unsafe-perm true
