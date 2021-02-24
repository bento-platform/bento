ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

LABEL Maintainer="Bento Project"

USER root

RUN apk update
RUN apk upgrade

RUN apk add --no-cache --virtual \
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
    libffi-dev \
	linux-headers \
	make \
    musl-dev \
    openssl-dev \
    python3-dev \
    postgresql-dev \
	postgresql-libs \
	perl \
	xz-dev \
	yaml-dev \
	zlib-dev

RUN python -m pip install --upgrade pip