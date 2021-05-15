FROM docker.io/alpine:3.12

ARG TARGETARCH=amd64

RUN echo $'\
@edge http://dl-cdn.alpinelinux.org/alpine/edge/main\n\
@edge http://dl-cdn.alpinelinux.org/alpine/edge/testing\n\
@edge http://dl-cdn.alpinelinux.org/alpine/edge/community' >> /etc/apk/repositories

RUN apk add --no-cache \
      python3 py3-pip py3-setuptools py3-wheel \
      py3-pillow \
      py3-aiohttp \
      py3-magic \
      py3-sqlalchemy \
      py3-psycopg2 \
      py3-ruamel.yaml \
      py3-commonmark@edge \
      py3-alembic@edge \
      # encryption
      olm-dev \
      py3-cffi \
      py3-pycryptodome \
      py3-unpaddedbase64 \
      py3-future \
      # proxy support
      py3-pysocks \
      # Other dependencies
      ca-certificates \
      su-exec \
      bash \
      curl \
      jq && \
  curl -sLo yq https://github.com/mikefarah/yq/releases/download/3.3.2/yq_linux_${TARGETARCH} && \
  chmod +x yq && mv yq /usr/bin/yq

COPY requirements.txt /opt/mudtrix/requirements.txt
WORKDIR /opt/mudtrix
RUN apk add --virtual .build-deps python3-dev libffi-dev build-base \
 && pip3 install -r requirements.txt  \
 && apk del .build-deps

COPY . /opt/mudtrix
RUN apk add --no-cache git && pip3 install .[e2be] && apk del git \
  # This doesn't make the image smaller, but it's needed so that the `version` command works properly
  && cp mudtrix/example-config.yaml . && rm -rf mudtrix

ENV UID=1337 GID=1337
VOLUME /data

CMD ["/opt/mudtrix/docker-run.sh"]
