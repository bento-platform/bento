ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

# TODO: use python:3.x-alpine instead of buster
FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

# TODO: change USER
USER root

WORKDIR /variant

ARG REPO
ARG BRANCH
ARG TAG

RUN git clone "${REPO}" && \
    ls /variant

RUN mkdir -p /variant/data

WORKDIR /variant/bento_variant_service

RUN git fetch && \
    git checkout "${BRANCH}" && \
    git pull $(echo "${REPO} refs/tags/${TAG}:refs/tags/${TAG}")

RUN ["pip", "install", "-r", "requirements.txt"]


# Install BCF Tools
RUN wget https://github.com/samtools/bcftools/releases/download/1.9/bcftools-1.9.tar.bz2
RUN tar -vxjf bcftools-1.9.tar.bz2
WORKDIR /variant/bento_variant_service/bcftools-1.9
RUN make
ENV PATH="/variant/bento_variant_service/bcftools-1.9:${PATH}"


# Run
WORKDIR /variant/bento_variant_service/bento_variant_service

CMD ["flask", "run", "--host=0.0.0.0"]
