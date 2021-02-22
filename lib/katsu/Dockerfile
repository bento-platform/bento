ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

LABEL Maintainer="Bento Project"

# TODO: change USER
USER root

WORKDIR /

RUN mkdir /app
WORKDIR /app

ARG KATSU_REPO
ARG KATSU_TAG

# Clone the repo
RUN git clone "${KATSU_REPO}"

WORKDIR /app/katsu
RUN git fetch; \
    git checkout develop; \
    git submodule update --init

# Trigger this at run time 
# (now runs from docker-compose)
#CMD ["runserver", "0.0.0.0:8000"]
#

# Install dependencies
# -- fixes PEP 517 build error --
RUN pip install cryptography==2.8; \
# --
    pip install -r requirements.txt


# TEMP
COPY settings.py ./chord_metadata_service/metadata/settings.py

# # Pull subdirectories
# WORKDIR /app/katsu/chord_metadata_service/dats
# RUN git pull

# Navigate back to the main repo
# WORKDIR /app/katsu

# At runtime
#ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"]

