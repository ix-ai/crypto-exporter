FROM alpine:latest
LABEL maintainer="docker@ix.ai" \
      ai.ix.repository="ix.ai/crypto-exporter"

WORKDIR /app

COPY src/ /app

RUN apk --no-cache upgrade && \
    apk add --no-cache py3-prometheus-client \
                       py3-requests \
                       py3-cryptography \
                       py3-multidict \
                       py3-aiohttp \
                       py3-pip \
                       gcc \
                       musl-dev \
                       python3-dev && \
    pip3 install --no-cache-dir -r requirements.txt && \
    apk del --purge --no-cache gcc musl-dev python3-dev py3-pip

EXPOSE 9188

ENTRYPOINT ["python3", "/app/exporter.py"]
