ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

# TODO: change USER
USER root

RUN mkdir /wes; \
    # for temp data
    mkdir /wes/tmp; \
    mkdir /data

WORKDIR /wes

#RUN wget -cO - https://github.com/broadinstitute/cromwell/releases/download/55/womtool-55.jar > womtool.jar

COPY chord_services.json ./chord_services.json

ARG REPO
ARG BRANCH
ARG TAG

RUN git clone "${REPO}"
RUN ls /wes

WORKDIR /wes/bento_wes

RUN git config user.name "docker" && \
    git config user.email "docker@bento.v2" && \
    git fetch && \
    git checkout "${BRANCH}" && \ 
    git pull $(echo "${REPO}")
#refs/tags/${TAG}:refs/tags/${TAG}

RUN ["pip", "install", "-r", "requirements.txt"]

# Run
WORKDIR /wes/bento_wes/bento_wes

COPY chord_services.json ./chord_services.json
COPY startup.sh ./startup.sh

CMD ["sh", "startup.sh"]
