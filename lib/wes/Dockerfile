ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

# TODO: change USER
USER root

# Install samtools from github repos (htslib needed first)
RUN apk --update add jq ncurses-dev && \
    git clone https://github.com/samtools/htslib.git && \
    cd htslib && \
    git submodule update --init --recursive && \
    make && \
    make install && \
    cd .. && \
    git clone https://github.com/samtools/samtools.git && \
    cd samtools && \
    make && \
    make install && \
    cd .. && \
    rm -rf htslib samtools

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
    git checkout tags/${TAG}

RUN ["pip", "install", "-r", "requirements.txt"]

# Run
WORKDIR /wes/bento_wes/bento_wes

COPY chord_services.json ./chord_services.json
COPY startup.sh ./startup.sh

CMD ["sh", "startup.sh"]
