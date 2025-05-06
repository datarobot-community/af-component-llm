# This Dockerfile.local can built with the following command:
#   > docker build -f Dockerfile -t python311-genai-dev .
# where the 'python311-genai-dev' is the name of the image that will be created.

# This reproduces a open source variant of https://images.chainguard.dev/directory/image/python
# hadolint ignore=DL3007
FROM cgr.dev/chainguard/wolfi-base:latest AS chainguard_python_dev

ARG PYTHON_VERSION=3.11
SHELL ["/bin/sh", "-o", "pipefail", "-c"]
RUN echo "[Python $PYTHON_VERSION]"

ENV PATH="${PATH}:/sbin"
RUN apk update && apk upgrade
# Wolfi python image
# hadolint ignore=DL3018,DL3059
RUN apk add --no-cache ca-certificates-bundle gdbm glibc glibc-locale-posix \
ld-linux libbz2-1 libcrypto3 libexpat1 libffi libgcc libssl3 libstdc++ \
mpdecimal ncurses ncurses-terminfo readline sqlite-libs \
wolfi-baselayout xz zlib
# Wolfi python dev image
# hadolint ignore=DL3018,DL3059
RUN apk add --no-cache apk-tools  bash  binutils  build-base  busybox  cyrus-sasl  \
gcc  git  glibc-dev  gmp  heimdal-libs  isl  keyutils-libs  \
krb5-conf  krb5-libs  libatomic  libbrotlicommon1  libbrotlidec1  \
libcom_err  libcrypt1  libcurl-openssl4  libgo  libgomp  libidn2  \
libldap  libnghttp2-14  libpcre2-8-0  libpsl  libquadmath  libstdc++-dev  \
libunistring  libverto  libxcrypt  libxcrypt-dev  libzstd1  \
linux-headers  make  mpc  mpfr  nss-db  nss-hesiod  \
openssf-compiler-options  pkgconf  posix-cc-wrappers  wget
# Python
# hadolint ignore=DL3018,DL3059
RUN apk add --no-cache \
    python-$PYTHON_VERSION \
    python-$PYTHON_VERSION-base \
    py$PYTHON_VERSION-pip \
    py3-pip-wheel
# Python dev
# hadolint ignore=DL3018,DL3059
RUN apk add --no-cache python-$PYTHON_VERSION-dev \
    python-$PYTHON_VERSION-base-dev \
    py$PYTHON_VERSION-pip-base \
    py$PYTHON_VERSION-setuptools

FROM chainguard_python_dev AS base

ENV VIRTUAL_ENV=/opt/venv

# hadolint ignore=DL3045
COPY requirements.txt requirements.txt

RUN sh -c "python -m venv ${VIRTUAL_ENV} && \
    . ${VIRTUAL_ENV}/bin/activate && \
    python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt"

ENV PATH=${VIRTUAL_ENV}/bin:${PATH}
ENV HOME=/opt
ENV CODE_DIR=/opt/code
ENV ADDRESS=0.0.0.0:8080

# This makes print statements show up in the logs API
ENV WITH_ERROR_SERVER=1 \
    PYTHONUNBUFFERED=1

COPY ./*.sh ${CODE_DIR}/
WORKDIR ${CODE_DIR}

ENTRYPOINT ["sh", "-c", "exec ${CODE_DIR}/start_server.sh \"$@\"", "--"]
