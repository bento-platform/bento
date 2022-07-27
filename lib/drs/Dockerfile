ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

# TODO: change USER
USER root

RUN mkdir /drs && \
    mkdir /wes;

WORKDIR /drs

ARG REPO
ARG BRANCH
ARG TAG

RUN git clone --depth 1 -b "${TAG:-$BRANCH}" "${REPO}" && \
    ls /drs

WORKDIR /drs/bento_drs

RUN mkdir -p /drs/bento_drs/data/obj && \
    mkdir -p /drs/bento_drs/data/db;

# Remove comment if custom requirements are needed
#COPY requirements.txt ./requirements.txt

RUN ["pip", "install", "-r", "requirements.txt"]

# Run
WORKDIR /drs/bento_drs/chord_drs

COPY startup.sh ./startup.sh

CMD ["sh", "startup.sh"]
