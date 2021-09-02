ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

# TODO: change USER
USER root

RUN mkdir /service-registry
WORKDIR /service-registry

ARG REPO
ARG BRANCH
ARG TAG

RUN git clone "${REPO}" && \
    ls /service-registry

WORKDIR /service-registry/bento_service_registry

RUN git fetch && \
    git checkout "${BRANCH}" && \
    git checkout tags/${TAG}

RUN pip install -r requirements.txt

COPY chord_services.json /service-registry/bento_service_registry/bento_service_registry/chord_services.json

# Run
WORKDIR /service-registry/bento_service_registry

COPY ./gunicorn_starter.sh .
RUN chmod 775 ./gunicorn_starter.sh

ENTRYPOINT [ "./gunicorn_starter.sh" ]
