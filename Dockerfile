FROM registry.gitlab.com/ix.ai/alpine:latest:latest
ARG CCXT
ARG PORT

RUN apk add --no-cache python3-dev libffi-dev openssl-dev && \
    pip3 install --no-cache-dir "ccxt<=${CCXT}"

ENV LOGLEVEL=INFO PORT=${PORT}

COPY src/exporter.py /

EXPOSE ${PORT}

ENTRYPOINT ["python3", "/exporter.py"]
