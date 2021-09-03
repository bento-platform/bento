ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

# TODO: change USER
USER root

RUN mkdir /logging
WORKDIR /logging

ARG REPO
ARG BRANCH
ARG TAG

RUN git clone "${REPO}"
RUN ls /logging

WORKDIR /logging/bento_log_service

RUN git fetch && \
    git checkout "${BRANCH}" && \
    git checkout tags/${TAG}

RUN ["pip", "install", "-r", "requirements.txt"]

# Run
WORKDIR /logging/bento_log_service

COPY chord_services.json ./chord_services.json

COPY ./gunicorn_starter.sh .
RUN chmod 775 ./gunicorn_starter.sh

ENTRYPOINT [ "./gunicorn_starter.sh" ]
