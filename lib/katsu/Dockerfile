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

# Clone the repo
RUN git clone "${KATSU_REPO}"

WORKDIR /app/katsu

RUN git config user.name "docker" && \
    git config user.email "docker@bento.v2" && \
    git fetch && \
    git checkout "${KATSU_BRANCH}" && \ 
    git pull $(echo "${KATSU_REPO}") && \
    git submodule update --init


# Install dependencies
# -- fixes PEP 517 build error --
RUN ["sed", "-i", "15s/.*/cryptography==2.8/", "requirements.txt"]
# --
RUN pip install -r requirements.txt;


# TEMP
ARG BENTOV2_DOMAIN
RUN sed -i "s/CHORD_HOST = urlparse(CHORD_URL or \"\").netloc/CHORD_HOST = \"${BENTOV2_DOMAIN}\"/" ./chord_metadata_service/metadata/settings.py

# # Pull subdirectories
# WORKDIR /app/katsu/chord_metadata_service/dats
# RUN git pull

# Navigate back to the main repo
# WORKDIR /app/katsu

# At runtime
#ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"]

