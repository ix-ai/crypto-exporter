FROM hub.ix.ai/docker/alpine:latest
LABEL ai.ix.maintainer="docker@ix.ai"

RUN apk add --no-cache python3-dev libffi-dev openssl-dev && \
    pip3 install ccxt

ENV LOGLEVEL=INFO

COPY exporter.py /

EXPOSE 9308

ENTRYPOINT ["python3", "/exporter.py"]
