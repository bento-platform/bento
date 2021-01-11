ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

USER root

RUN apt-get update
RUN apt-get install git nginx -y
# \
#            npm
RUN apt-get upgrade -y

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

# temp (for dev only)
#ENTRYPOINT [ "npm", "run", "watch" ]
CMD ["nginx", "-g", "daemon off;"]
