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
RUN git fetch
RUN git checkout "${BRANCH}"
RUN git pull $(echo "${REPO} refs/tags/${TAG}:refs/tags/${TAG}")

COPY requirements.txt ./requirements.txt

RUN ["pip", "install", "-r", "requirements.txt"]

# Run
WORKDIR /logging/bento_log_service/bento_log_service

COPY chord_services.json ./chord_services.json

CMD ["flask", "run", "--host=0.0.0.0"]
