ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

USER root

RUN apk update
# RUN apk upgrade

RUN apk add git
RUN apk add --no-cache postgresql-libs
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev libffi-dev
# RUN apk add postgresql-dev

#RUN apt-get update
#RUN apt-get upgrade

#RUN apt-get install git


RUN mkdir /service-registry
WORKDIR /service-registry

ARG REPO
ARG BRANCH
ARG TAG

#RUN git clone "${REPO}"
COPY bento_service_registry  /service-registry/bento_service_registry
RUN ls /service-registry
WORKDIR /service-registry/bento_service_registry
#RUN git fetch
#RUN git checkout "${BRANCH}"
#RUN git pull $(echo "${REPO} refs/tags/${TAG}:refs/tags/${TAG}")

RUN pip install -r requirements.txt

COPY chord_services.json  /service-registry/bento_service_registry/chord_services.json

WORKDIR /service-registry/bento_service_registry


# Run
CMD ["flask", "run", "--host=0.0.0.0"]
