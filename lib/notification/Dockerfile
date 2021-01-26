ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

# TODO: change USER
USER root

RUN apk update
RUN apk upgrade

RUN apk add git 
RUN apk add --no-cache postgresql-libs
RUN apk add --no-cache --virtual .build-deps gcc musl-dev make postgresql-dev redis
#libffi-dev zlib-dev bzip2-dev xz-dev 
ENV LIBRARY_PATH=/lib:/usr/lib

WORKDIR /notification

# # Create data directory
RUN mkdir -p /notification/data

ARG REPO
ARG BRANCH
ARG TAG

RUN git clone "${REPO}"
RUN ls /notification

WORKDIR /notification/bento_notification_service
RUN git fetch
RUN git checkout "${BRANCH}"
RUN git pull $(echo "${REPO} refs/tags/${TAG}:refs/tags/${TAG}")

RUN ["pip", "install", "-r", "requirements.txt"]


# Run
WORKDIR /notification/bento_notification_service/bento_notification_service

#CMD ["redis-server", "&;", "flask", "run", "--host=0.0.0.0"]
#CMD ["flask", "db", "upgrade"]
COPY startup.sh ./startup.sh

ENTRYPOINT [ "sh", "./startup.sh" ]