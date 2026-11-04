FROM python:3.14-slim

WORKDIR /bentoctl

# docker compose config (used by py_bentoctl/config.py to enumerate enabled services) needs the
# docker CLI + compose plugin present, even though no daemon is running in this container.
# Debian's own `docker.io` package doesn't ship a `docker` client binary, so we use Docker's
# official apt repo instead, and only install the CLI + compose plugin (no engine/daemon).
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates curl gnupg && \
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
        > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends docker-ce-cli docker-compose-plugin && \
    rm -rf /var/lib/apt/lists/*

COPY py_bentoctl py_bentoctl
COPY requirements.txt .
COPY bentoctl.bash .
COPY docker-compose.yaml .
COPY lib lib
COPY etc/default_config.env etc/default_config.env
COPY etc/bento.env etc/bento.env
COPY etc/bento_post_config.bash etc/bento_post_config.bash
COPY etc/bento_services.json etc/bento_services.json

RUN chmod +x bentoctl.bash

# Create and activate a venv, then install Python dependencies into it
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Create a `bentoctl` shell alias for bentoctl.bash
RUN echo "alias bentoctl='/bentoctl/bentoctl.bash'" >> /etc/bash.bashrc

# Use an interactive shell as the entrypoint so the alias above is picked up
# even for non-interactive `docker run <image> bentoctl` invocations.
ENTRYPOINT [ "/bin/bash", "-ic" ]