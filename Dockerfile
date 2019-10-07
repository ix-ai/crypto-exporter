FROM alpine:latest
LABEL maintainer="docker@ix.ai"

WORKDIR /app

COPY src/ /app

RUN apk --no-cache upgrade && \
    apk add --no-cache python3 gcc musl-dev python3-dev libffi-dev openssl-dev && \
    pip3 install --no-cache-dir -r requirements.txt && \
    apk del --purge --no-cache gcc musl-dev python3-dev libffi-dev openssl-dev

EXPOSE 9188

ENTRYPOINT ["python3", "/app/exporter.py"]
