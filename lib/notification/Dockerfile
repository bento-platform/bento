ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

# TODO: change USER
USER root

WORKDIR /notification

# Create data directory
RUN mkdir -p /notification/data

ARG REPO
ARG BRANCH
ARG TAG

RUN git clone "${REPO}"
RUN ls /notification

WORKDIR /notification/bento_notification_service

RUN git fetch && \
    git checkout "${BRANCH}" && \
    git pull $(echo "${REPO} refs/tags/${TAG}:refs/tags/${TAG}")

RUN ["pip", "install", "-r", "requirements.txt"]


# Run
WORKDIR /notification/bento_notification_service/bento_notification_service

COPY startup.sh ./startup.sh

ENTRYPOINT [ "sh", "./startup.sh" ]