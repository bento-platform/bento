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
ARG BRANCH
ARG TAG

RUN git clone "${REPO}" && \
    ls /federation

WORKDIR /federation/bento_federation_service

RUN git fetch && \
    git checkout "${BRANCH}" && \
    git pull $(echo "${REPO} refs/tags/${TAG}:refs/tags/${TAG}")

RUN ["pip", "install", "-r", "requirements.txt"]

# Run
WORKDIR /federation/bento_federation_service

# -- Temp
# Modify search code to not validate self-signed dev cert
RUN sed -i 's/body=request_body,/body=request_body,validate_cert=False,/g' ./bento_federation_service/utils.py;
# --

CMD ["python", "run.py"]
