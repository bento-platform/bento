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
ARG BRANCH
ARG TAG

RUN git clone "${REPO}"

WORKDIR /event-relay/bento_event_relay
RUN git fetch && \
    git checkout "${BRANCH}" && \
    git pull $(echo "${REPO} refs/tags/${TAG}:refs/tags/${TAG}")

RUN ["npm", "install"]

# Run
WORKDIR /event-relay/bento_event_relay
CMD ["npm", "start"]