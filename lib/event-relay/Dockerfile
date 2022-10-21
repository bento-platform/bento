ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

# TODO: change USER
USER root

ENV LIBRARY_PATH=/lib:/usr/lib

RUN apk add git

WORKDIR /event-relay

# Create data directory
RUN mkdir -p /event-relay/data

ARG REPO
ARG TAG_OR_BRANCH

RUN git clone ${REPO} --depth 1 -b ${TAG_OR_BRANCH}


WORKDIR /event-relay/bento_event_relay

RUN ["npm", "install"]

# Run
CMD ["npm", "start"]