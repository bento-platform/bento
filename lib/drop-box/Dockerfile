ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

USER root

# RUN apk update
# RUN apk upgrade

# RUN apk add git
# RUN apk add postgresql-dev

RUN apt-get update
#RUN apt-get upgrade

RUN apt-get install git


RUN mkdir /drop-box
WORKDIR /drop-box

ARG REPO
ARG BRANCH
ARG TAG

RUN git clone "${REPO}"
RUN ls /drop-box
WORKDIR /drop-box/bento_drop_box_service
RUN git fetch
RUN git checkout "${BRANCH}"
RUN git pull $(echo "${REPO} refs/tags/${TAG}:refs/tags/${TAG}")

RUN pip install -r requirements.txt

WORKDIR /drop-box/bento_drop_box_service

# Run
CMD ["flask", "run", "--host=0.0.0.0"]
