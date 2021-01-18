ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

LABEL Maintainer="Bento Project"

COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf

# Temp: dev dir, TODO: use ARG instead
COPY ./certs/dev/auth/auth_fullchain1.crt /usr/local/openresty/nginx/certs/auth_fullchain1.crt
COPY ./certs/dev/auth/auth_privkey1.key /usr/local/openresty/nginx/certs/auth_privkey1.key

COPY ./certs/dev/fullchain1.crt /usr/local/openresty/nginx/certs/fullchain1.crt
COPY ./certs/dev/privkey1.key /usr/local/openresty/nginx/certs/privkey1.key


COPY node_info.lua /usr/local/openresty/nginx/node_info.lua
COPY proxy_auth.lua /usr/local/openresty/nginx/proxy_auth.lua


COPY instance_auth.json /usr/local/openresty/nginx/instance_auth.json
COPY instance_config.json /usr/local/openresty/nginx/instance_config.json
COPY auth_config.json /usr/local/openresty/nginx/auth_config.json



# Update and install dependencies
RUN apk update
RUN /usr/local/openresty/luajit/bin/luarocks install lua-resty-openidc
