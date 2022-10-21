ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

# TODO: change USER
USER root

WORKDIR /notification

# Create data directory
RUN mkdir -p /notification/data

ARG REPO
ARG TAG_OR_BRANCH

RUN git clone ${REPO} --depth 1 -b ${TAG_OR_BRANCH}
RUN ls /notification

WORKDIR /notification/bento_notification_service

RUN ["pip", "install", "-r", "requirements.txt"]

# Run
COPY startup.sh ./startup.sh
ENTRYPOINT [ "sh", "./startup.sh" ]