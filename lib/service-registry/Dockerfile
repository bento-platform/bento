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

RUN git clone --depth 1 -b "${TAG:-$BRANCH}" "${REPO}" && \
    ls /service-registry

WORKDIR /service-registry/bento_service_registry

RUN pip install -r requirements.txt

# Run
WORKDIR /service-registry/bento_service_registry

COPY chord_services.json .

COPY ./gunicorn_starter.sh .
RUN chmod 775 ./gunicorn_starter.sh

CMD [ "./gunicorn_starter.sh" ]
