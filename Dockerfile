FROM hub.ix.ai/docker/alpine:latest
LABEL ai.ix.maintainer="docker@ix.ai"
ARG CCXT
ARG PORT

RUN apk add --no-cache python3-dev libffi-dev openssl-dev && \
    pip3 install --no-cache-dir "ccxt<=${CCXT}" pygelf

ENV LOGLEVEL=INFO PORT=${PORT}

COPY src/exporter.py /

EXPOSE ${PORT}

ENTRYPOINT ["python3", "/exporter.py"]
