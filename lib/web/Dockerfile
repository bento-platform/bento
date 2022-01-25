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

COPY nginx.conf /etc/nginx/conf.d/nginx.conf

RUN mkdir /web
WORKDIR /web

ARG BENTO_WEB_REPO
ARG BENTO_WEB_BRANCH
ARG BENTO_WEB_TAG

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
        git clone "${BENTO_WEB_REPO}"; \
        pwd ; ls -la ; \
        \
        cd ./bento_web ; \
        pwd ; ls -la ; \
        \
        git fetch ; \
        git checkout "${BENTO_WEB_BRANCH}" ; \
        git checkout tags/${BENTO_WEB_TAG} ; \
        git pull ; \
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
RUN mkdir /run/nginx && \
    touch /run/nginx/nginx.pid && \
    npm config set unsafe-perm true
