FROM golang:1.24-bookworm

ARG HUGO_VERSION=0.159.1

RUN apt-get update \
    && apt-get install -y --no-install-recommends wget ca-certificates git \
    && wget -O /tmp/hugo.deb "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.deb" \
    && apt-get install -y /tmp/hugo.deb \
    && rm -f /tmp/hugo.deb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /site

COPY . /site

EXPOSE 1313

CMD ["hugo", "server", "--bind", "0.0.0.0", "--port", "1313", "--disableKinds", "rss"]
