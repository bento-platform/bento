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
ARG KATSU_BRANCH
ARG KATSU_TAG

ARG PROJECT_DIRECTORY

# Clone the repo
RUN git clone "${KATSU_REPO}"

WORKDIR ${PROJECT_DIRECTORY}

RUN git config user.name "docker" && \
    git config user.email "docker@bento.v2" && \
    git fetch && \
    git checkout "${KATSU_BRANCH}" && \
    git checkout tags/${KATSU_TAG} && \
    git submodule update --init


# Install dependencies
# -- fixes PEP 517 build error --
RUN ["sed", "-i", "15s/.*/cryptography==2.8/", "requirements.txt"]
# --
RUN pip install -r requirements.txt;


# TEMP: modify settings.py file to allow for 
# localhost+port & domain host name to be allowed to make calls
ARG BENTOV2_DOMAIN
RUN sed -i "s/CHORD_HOST = urlparse(CHORD_URL or \"\").netloc/CHORD_HOST = \"${BENTOV2_DOMAIN}\"/" ${PROJECT_DIRECTORY}/chord_metadata_service/metadata/settings.py
RUN sed -i "s/\[CHORD_HOST or \"localhost\"\]/\[CHORD_HOST or \"localhost:8000\"\]/" ${PROJECT_DIRECTORY}/chord_metadata_service/metadata/settings.py
