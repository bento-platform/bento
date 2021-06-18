ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

USER root

RUN apk update && \
    apk add git nginx && \
    apk upgrade

COPY nginx.conf /etc/nginx/conf.d/nginx.conf

RUN mkdir /web
WORKDIR /web

ARG BENTO_WEB_REPO
ARG BENTO_WEB_BRANCH

ARG BENTO_WEB_IS_DEBUG

#RUN mkdir bento_web/
RUN if [ "$BENTO_WEB_IS_DEBUG" = "true" ] ; then \
        echo "Building Web in Development Mode" ; \
    \
    else \
        echo "Building Web in Production Mode" ; \
        \
        git clone "${BENTO_WEB_REPO}" && \
        \
        cd ./bento_web && \
        \
        git fetch && \
        git checkout "${BENTO_WEB_BRANCH}" && \
        git pull ; \
        \
        rm -rf npm-shrinkwrap.json node_modules && \
        npm cache clean --force && \
        npm cache verify && \
        npm install --save -g --unsafe-perm=true --allow-root; \
    fi


# Copy startup scripts

# TODO: parameterize and only copy the 
# one that is used
COPY ./dev_startup.sh /web/dev_startup.sh
COPY ./startup.sh /web/startup.sh

WORKDIR /web/bento_web

# fix crash at runtime
RUN mkdir /run/nginx && \
    touch /run/nginx/nginx.pid && \
    npm config set unsafe-perm true
