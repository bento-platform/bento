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
    git checkout tags/${TAG}

RUN ["pip", "install", "-r", "requirements.txt"]


# Install BCF Tools
ARG BCFTOOLS_VERSION

RUN wget https://github.com/samtools/bcftools/releases/download/${BCFTOOLS_VERSION}/bcftools-${BCFTOOLS_VERSION}.tar.bz2
RUN tar -vxjf bcftools-${BCFTOOLS_VERSION}.tar.bz2

WORKDIR /variant/bento_variant_service/bcftools-${BCFTOOLS_VERSION}
RUN make
ENV PATH="/variant/bento_variant_service/bcftools-${BCFTOOLS_VERSION}:${PATH}"



# Run
WORKDIR /variant/bento_variant_service

# CMD ["flask", "run", "--host=0.0.0.0"]
COPY ./gunicorn_starter.sh .
RUN chmod 775 ./gunicorn_starter.sh

CMD [ "./gunicorn_starter.sh" ]
