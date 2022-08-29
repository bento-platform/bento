ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

USER root

ARG BENTO_WEB_USER
RUN adduser --disabled-password "$BENTO_WEB_USER"
ENV BENTO_WEB_USER="$BENTO_WEB_USER"

RUN apk update && \
    apk add git nginx && \
    apk upgrade

# as of  BENTOV2_WEB_BASE_IMAGE_VERSION=16.13-alpine3.15 ,
# override default nginx.conf file
COPY nginx.conf /etc/nginx/nginx.conf

RUN mkdir /web
WORKDIR /web

ARG BENTO_WEB_REPO
ARG BENTO_WEB_TAG_OR_BRANCH

ARG BENTO_WEB_IS_DEBUG

ARG BENTO_CUSTOM_HEADER
ENV CUSTOM_HEADER=$BENTO_CUSTOM_HEADER

#RUN mkdir bento_web/
RUN if [ "$BENTO_WEB_IS_DEBUG" = "true" ] ; then \
        echo "Building Web in Development Mode" ; \
        mkdir bento_web ; \
    \
    else \
        echo "Building Web in Production Mode" ; \
        pwd ; ls -la ; \
        \
        git clone ${BENTO_WEB_REPO} --depth 1 -b ${BENTO_WEB_TAG_OR_BRANCH}; \
        pwd ; ls -la ; \
        \
        cd ./bento_web ; \
        pwd ; ls -la ; \
        \
        rm -rf npm-shrinkwrap.json node_modules ; \
        npm cache clean --force ; \
        npm cache verify ; \
        npm install --save --unsafe-perm=true --allow-root; \
    fi


# Copy startup scripts

# TODO: parameterize and only copy the
# one that is used
COPY ./dev_startup.sh /web/dev_startup.sh
COPY ./startup.sh /web/startup.sh

# fix crash at runtime
RUN mkdir -p /run/nginx && \
    touch /run/nginx/nginx.pid && \
    npm config set unsafe-perm true
