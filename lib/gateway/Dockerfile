ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

LABEL Maintainer="Bento Project"

COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf


# LUA stuff
COPY node_info.lua /usr/local/openresty/nginx/node_info.lua
COPY proxy_auth.lua /usr/local/openresty/nginx/proxy_auth.lua

COPY instance_config.json /usr/local/openresty/nginx/instance_config.json
COPY auth_config.json /usr/local/openresty/nginx/auth_config.json


# Update and install dependencies
RUN apk update && \
    apk add git && \
    /usr/local/openresty/luajit/bin/luarocks install lua-resty-openidc
