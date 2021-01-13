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
RUN git fetch
RUN git checkout "${BENTO_WEB_BRANCH}"
RUN git pull

RUN rm -rf package-lock.json npm-shrinkwrap.json node_modules
RUN npm cache clean --force
RUN npm cache verify
RUN npm install

RUN npm run build

# fix crash at runtime
RUN mkdir /run/nginx
RUN touch /run/nginx/nginx.pid 
#\ && chown -R api-gatway:api-gatway /run/nginx.pid /cache/nginx

# Run
CMD ["nginx", "-g", "daemon off;"]
