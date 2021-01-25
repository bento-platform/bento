ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

# TODO: change USER
USER root

RUN apk update
RUN apk upgrade

RUN apk add git 
RUN apk add --no-cache postgresql-libs
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev libffi-dev

# RUN apt-get update
# #RUN apt-get upgrade

# RUN apt-get install git


RUN mkdir /drs
WORKDIR /drs

ARG REPO
ARG BRANCH
ARG TAG

RUN git clone "${REPO}"
RUN ls /drs

WORKDIR /drs/chord_drs
RUN git fetch
RUN git checkout "${BRANCH}"
RUN git pull $(echo "${REPO} refs/tags/${TAG}:refs/tags/${TAG}")

# Remove comment if custom requirements are needed
#COPY requirements.txt ./requirements.txt

RUN ["pip", "install", "-r", "requirements.txt"]

# Run
WORKDIR /drs/chord_drs/chord_drs

CMD ["flask", "run", "--host=0.0.0.0"]
