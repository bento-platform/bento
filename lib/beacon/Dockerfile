ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

# TODO: change USER
USER root

ARG BEACON_REPO
ARG BEACON_TAG_OR_BRANCH

RUN mkdir /beacon
WORKDIR /beacon

RUN git clone ${BEACON_REPO} --depth 1 -b ${BEACON_TAG_OR_BRANCH}

WORKDIR /beacon/bento_beacon

RUN pip install -r requirements.txt

# copy config files 
COPY config /beacon/bento_beacon/bento_beacon/config_files/

COPY ./gunicorn_starter.sh .
RUN chmod 775 ./gunicorn_starter.sh

CMD [ "./gunicorn_starter.sh" ]