ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

LABEL Maintainer="Bento Project"

WORKDIR /

USER root

# Install dependencies
RUN apk update

RUN apk add --no-cache \
	gcc musl-dev libffi-dev openssl-dev python3-dev \
	autoconf \
	automake \
	bash \
	build-base \
	bzip2-dev \
	curl \
	curl-dev \
	gcc \
	git \
	libcurl \
	libressl-dev \
	linux-headers \
	make \
	musl-dev \
	perl \
	xz-dev \
	yaml-dev \
	zlib-dev

RUN apk add postgresql-dev \
	postgresql-libs

RUN mkdir /app
WORKDIR /app


ARG KATSU_REPO
ARG KATSU_TAG

# Clone the repo
RUN git clone "${KATSU_REPO}"

RUN ls
WORKDIR /app/katsu
RUN git fetch
RUN git checkout develop
RUN git submodule update --init

# Trigger this at run time
#CMD ["runserver", "0.0.0.0:8000"]
#

# Install dependencies
RUN pip install -r requirements.txt

# TEMP
COPY settings.py ./chord_metadata_service/metadata/settings.py

# # Pull subdirectories
# WORKDIR /app/katsu/chord_metadata_service/dats
# RUN git pull

# Navigate back to the main repo
# WORKDIR /app/katsu

# At runtime
#ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"]

