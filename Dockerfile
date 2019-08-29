FROM alpine:latest
LABEL maintainer="docker@ix.ai"

ARG PORT=9308
ARG LOGLEVEL=INFO

WORKDIR /app

COPY src/ /app

RUN apk --no-cache upgrade && \
    apk add --no-cache python3 gcc musl-dev python3-dev libffi-dev openssl-dev && \
    pip3 install --no-cache-dir -r requirements.txt

ENV LOGLEVEL=${LOGLEVEL} PORT=${PORT}

EXPOSE ${PORT}

ENTRYPOINT ["python3", "/app/exporter.py"]
