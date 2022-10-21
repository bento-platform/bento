ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

# TODO: change
USER root

RUN mkdir /drop-box
WORKDIR /drop-box

ARG REPO
ARG TAG_OR_BRANCH

RUN git clone ${REPO} --depth 1 -b ${TAG_OR_BRANCH}  && \
    ls /drop-box;
WORKDIR /drop-box/bento_drop_box_service

RUN pip install -r requirements.txt

WORKDIR /drop-box/bento_drop_box_service

COPY ./gunicorn_starter.sh .
RUN chmod 775 ./gunicorn_starter.sh

# Run
ENTRYPOINT [ "./gunicorn_starter.sh" ]
