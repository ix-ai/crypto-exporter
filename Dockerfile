FROM alpine:latest
LABEL maintainer="docker@ix.ai"

ARG CCXT=1.18.928
ARG PORT=9308
ARG LOGLEVEL=INFO

RUN apk --no-cache upgrade && \
    apk add --no-cache python3 gcc musl-dev python3-dev libffi-dev openssl-dev && \
    pip3 install --no-cache-dir "ccxt<=${CCXT}" prometheus_client pygelf

ENV LOGLEVEL=${LOGLEVEL} PORT=${PORT}

COPY src/exporter.py /

EXPOSE ${PORT}

ENTRYPOINT ["python3", "/exporter.py"]
