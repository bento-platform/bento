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

RUN git clone "${REPO}" && \
    ls /drs

WORKDIR /drs/chord_drs

RUN git fetch && \
    git checkout "${BRANCH}" &&  \
    git checkout tags/${TAG} && \
    \
    mkdir -p /drs/chord_drs/data/obj && \
    mkdir -p /drs/chord_drs/data/db;
#     git pull $(echo "${REPO} refs/tags/${TAG}:refs/tags/${TAG}") && \

# Remove comment if custom requirements are needed
#COPY requirements.txt ./requirements.txt

RUN ["pip", "install", "-r", "requirements.txt"]

# Run
WORKDIR /drs/chord_drs/chord_drs

COPY startup.sh ./startup.sh

CMD ["sh", "startup.sh"]
