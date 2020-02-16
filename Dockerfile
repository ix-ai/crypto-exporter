FROM alpine:latest
LABEL maintainer="docker@ix.ai" \
      ai.ix.repository="ix.ai/crypto-exporter"

COPY exporter/requirements.txt /exporter/requirements.txt

RUN apk --no-cache upgrade && \
    apk add --no-cache py3-prometheus-client \
                       py3-requests \
                       py3-cryptography \
                       py3-multidict \
                       py3-aiohttp \
                       py3-pip \
                       py3-toml \
                       py3-numpy \
                       py3-pynacl \
                       py3-urllib3 \
                       py3-yarl && \
    apk add --no-cache python3-dev gcc musl-dev libffi-dev make && \
    pip3 install --no-cache-dir -r exporter/requirements.txt && \
    apk del --purge --no-cache gcc musl-dev python3-dev py3-pip libffi-dev

COPY exporter/ /exporter
COPY crypto-exporter.sh /usr/local/bin/crypto-exporter.sh

EXPOSE 9188

ENTRYPOINT ["/usr/local/bin/crypto-exporter.sh"]
