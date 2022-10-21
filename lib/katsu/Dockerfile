ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

LABEL Maintainer="Bento Project"

# TODO: change USER
USER root

WORKDIR /

RUN mkdir /app && \
    mkdir /app/tmp && \
    chmod 777 /app/tmp

WORKDIR /app

ARG KATSU_REPO
ARG TAG_OR_BRANCH

ARG PROJECT_DIRECTORY

# Clone the repo
RUN git clone ${KATSU_REPO} --depth 1 -b ${TAG_OR_BRANCH}

WORKDIR ${PROJECT_DIRECTORY}

RUN git config user.name "docker" && \
    git config user.email "docker@bento.v2" && \
    git submodule update --init


# Install dependencies
RUN pip install -r requirements.txt;


# TEMP: modify settings.py file to allow for
# localhost+port & domain host name to be allowed to make calls
ARG BENTOV2_PORTAL_DOMAIN
RUN sed -i "s/CHORD_HOST = urlparse(CHORD_URL or \"\").netloc/CHORD_HOST = \"${BENTOV2_PORTAL_DOMAIN}\"/" ${PROJECT_DIRECTORY}/chord_metadata_service/metadata/settings.py
RUN sed -i "s/\[CHORD_HOST or \"localhost\"\]/\[CHORD_HOST, \"localhost\"\]/" ${PROJECT_DIRECTORY}/chord_metadata_service/metadata/settings.py
