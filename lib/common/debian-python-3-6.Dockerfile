ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

LABEL Maintainer="Bento Project"

USER root

RUN apt-get update; \
	apt-get upgrade; \
	apt-get install -y \
		autoconf \
		automake \
		bash \
		cargo \
		curl \
		gcc \
		git \
		libffi-dev \
		make \
		musl-dev \
		perl 

RUN python -m pip install --upgrade pip
RUN pip install gunicorn