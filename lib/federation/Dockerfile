ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

# TODO: change USER
USER root

ENV LIBRARY_PATH=/lib:/usr/lib

WORKDIR /federation

# # Create data directory
RUN mkdir -p /federation/data

ARG REPO
ARG TAG_OR_BRANCH

RUN git clone ${REPO} --depth 1 -b ${TAG_OR_BRANCH} && \
    ls /federation
WORKDIR /federation/bento_federation_service

RUN ["pip", "install", "-r", "requirements.txt"]

# Run
WORKDIR /federation/bento_federation_service
CMD ["python", "run.py"]
