FROM alpine:latest as builder
COPY exporter/requirements.txt /work/exporter/requirements.txt

ENV CRYPTOGRAPHY_DONT_BUILD_RUST="1"

RUN set -xeu; \
    mkdir -p /work/wheels; \
    apk add \
      python3-dev \
      openssl-dev \
      gcc \
      musl-dev \
      libffi-dev \
      make \
      openssl-dev \
      cargo \
    ; \
    python3 -m ensurepip; \
    pip3 install -U \
      wheel \
      pip

RUN pip3 wheel --prefer-binary -r /work/exporter/requirements.txt -w /work/wheels

FROM alpine:latest
LABEL maintainer="docker@ix.ai"
LABEL ai.ix.repository="ix.ai/crypto-exporter"

COPY --from=builder /work /

RUN set -xeu; \
    ls -lashi /wheels; \
    apk add --no-cache python3; \
    python3 -m ensurepip; \
    pip3 install --no-cache-dir -U pip;\
    pip3 install \
      --no-index \
      --no-cache-dir \
      --find-links /wheels \
      --requirement /exporter/requirements.txt \
    ; \
    rm -rf /wheels; \
    addgroup crypto-exporter; \
    adduser -G crypto-exporter -D -H crypto-exporter

COPY crypto-exporter /usr/local/bin/crypto-exporter
COPY exporter /exporter

USER crypto-exporter:crypto-exporter

EXPOSE 9188

ENTRYPOINT ["/usr/local/bin/crypto-exporter"]
