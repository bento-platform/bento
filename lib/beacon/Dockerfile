ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

# TODO: change USER
USER root

ARG REPO
ARG BRANCH

RUN mkdir /beacon
WORKDIR /beacon

RUN git clone "${REPO}"

RUN git fetch && \
    git checkout "${BRANCH}"

WORKDIR /beacon/bento_beacon

RUN pip install -r requirements.txt

# copy config files 
ADD config .

COPY ./gunicorn_starter.sh .
RUN chmod 775 ./gunicorn_starter.sh

CMD [ "./gunicorn_starter.sh" ]