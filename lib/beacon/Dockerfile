ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

# TODO: change USER
USER root

ARG BEACON_REPO
ARG BEACON_BRANCH

RUN mkdir /beacon
WORKDIR /beacon

RUN git clone "${BEACON_REPO}"

WORKDIR /beacon/bento_beacon

RUN git fetch && \
    git checkout "${BEACON_BRANCH}"

RUN pip install -r requirements.txt

# copy config files 
ADD config /beacon/bento_beacon/bento_beacon/config_files

COPY ./gunicorn_starter.sh .
RUN chmod 775 ./gunicorn_starter.sh

CMD [ "./gunicorn_starter.sh" ]