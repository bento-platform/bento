ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

# TODO: change USER
USER root

RUN mkdir /drs;

WORKDIR /drs

ARG REPO
ARG BRANCH
ARG TAG

RUN git clone "${REPO}"
RUN ls /drs

WORKDIR /drs/chord_drs
RUN git fetch
RUN git checkout "${BRANCH}"
RUN git pull $(echo "${REPO} refs/tags/${TAG}:refs/tags/${TAG}")

RUN mkdir -p ./data/obj && \
    mkdir -p ./data/db;
# Remove comment if custom requirements are needed
#COPY requirements.txt ./requirements.txt

RUN ["pip", "install", "-r", "requirements.txt"]

# Run
WORKDIR /drs/chord_drs/chord_drs

# CMD ["flask", "run", "--host=0.0.0.0"]
COPY startup.sh ./startup.sh

CMD ["sh", "startup.sh"]
