FROM golang:1.24-bookworm

ARG HUGO_VERSION=0.159.1
ARG GO_VERSION=1.26.1

RUN apt-get update \
    && apt-get install -y --no-install-recommends wget ca-certificates git tar \
    && export DEB_ARCH="$(dpkg --print-architecture)" \
    && export GO_ARCH="${DEB_ARCH}" \
    && if [ "${DEB_ARCH}" = "amd64" ]; then GO_ARCH="amd64"; fi \
    && if [ "${DEB_ARCH}" = "arm64" ]; then GO_ARCH="arm64"; fi \
    && wget -O /tmp/go.tgz "https://dl.google.com/go/go${GO_VERSION}.linux-${GO_ARCH}.tar.gz" \
    && rm -rf /usr/local/go \
    && tar -C /usr/local -xzf /tmp/go.tgz \
    && rm -f /tmp/go.tgz \
    && wget -O /tmp/hugo.deb "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-${DEB_ARCH}.deb" \
    && apt-get install -y /tmp/hugo.deb \
    && rm -f /tmp/hugo.deb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /site

COPY . /site

EXPOSE 1313

CMD ["hugo", "server", "--bind", "0.0.0.0", "--port", "1313", "--disableKinds", "rss"]
