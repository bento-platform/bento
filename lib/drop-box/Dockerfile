ARG BASE_IMAGE
ARG BASE_IMAGE_VERSION

FROM "${BASE_IMAGE}:${BASE_IMAGE_VERSION}"

# TODO: change
USER root

RUN mkdir /drop-box
WORKDIR /drop-box

ARG REPO
ARG BRANCH
ARG TAG

RUN git clone "${REPO}" && \
    ls /drop-box;
WORKDIR /drop-box/bento_drop_box_service
RUN git fetch && \
    git checkout "${BRANCH}" &&  \
    git checkout tags/${TAG}

# Remove comment if custom requirements are needed
COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

WORKDIR /drop-box/bento_drop_box_service

# Run
CMD ["flask", "run", "--host=0.0.0.0"]
