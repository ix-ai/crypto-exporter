# crypto-exporter

[![Pipeline Status](https://gitlab.com/ix.ai/crypto-exporter/badges/master/pipeline.svg)](https://gitlab.com/ix.ai/crypto-exporter/)
[![Docker Stars](https://img.shields.io/docker/stars/ixdotai/crypto-exporter.svg)](https://hub.docker.com/r/ixdotai/crypto-exporter/)
[![Docker Pulls](https://img.shields.io/docker/pulls/ixdotai/crypto-exporter.svg)](https://hub.docker.com/r/ixdotai/crypto-exporter/)
[![Gitlab Project](https://img.shields.io/badge/GitLab-Project-554488.svg)](https://gitlab.com/ix.ai/crypto-exporter/)

Prometheus exporter, written in python, for different crypto exchanges

## Usage
```sh
docker run --rm -it -p 9999:9999 \
  -e EXCHANGE="poloniex" \
  -e LOGLEVEL=DEBUG \
  -e API_KEY="your_api_key" \
  -e API_SECRET="your_api_secret" \
  -e PORT=9999
  -e GELF_HOST="graylog" \
  --name poloniex-exporter
  registry.gitlab.com/ix.ai/crypto-exporter:latest
```
Or use the image from `ixdotai/crypto-exporter`
```sh
docker run --rm -it -p 9999:9999 \
  -e EXCHANGE="poloniex" \
  -e LOGLEVEL=DEBUG \
  -e API_KEY="your_api_key" \
  -e API_SECRET="your_api_secret" \
  -e PORT=9999
  -e GELF_HOST="graylog" \
  --name poloniex-exporter
  ixdotai/crypto-exporter:latest
```

## Docker Stack example
```yml
version: '3.7'

services:
  binance:
    image: ixdotai/crypto-exporter:latest
    networks:
      - exporters
      - graylog
    environment:
      EXCHANGE: binance
      GELF_HOST: tasks.graylog_graylog
      GELF_PORT: 12201
      API_KEY: your_api_key
      API_SECRET: your_api_secret
  bitfinex:
    image: registry.gitlab.com/ix.ai/crypto-exporter:latest
    networks:
      - exporters
      - graylog
    environment:
      EXCHANGE: bitfinex
      GELF_HOST: tasks.graylog_graylog
      GELF_PORT: 12201
      API_KEY: your_api_key
      API_SECRET: your_api_secret

networks:
  exporters:
    external: true
  graylog:
    external: true

```

### Prometheus configuration with DNS service discovery
```yml
scrape_configs:
- job_name: 'crypto-exporters'
  honor_timestamps: true
  scrape_interval: 30s
  scrape_timeout: 30s
  metrics_path: /metrics
  scheme: http
  dns_sd_configs:
  - names:
    - tasks.binance
    - tasks.bitfinex
```

Make sure that your prometheus server is able to reach the network set for the crypto-exporter.

**Warning**: some exchanges (notably: gdax/coinbasepro) need more than 30s to scrape

### Supported variables
| **Variable**  | **Default** | **Mandatory** | **Description**                                                                                                        |
|:--------------|:-----------:|:-------------:|:-----------------------------------------------------------------------------------------------------------------------|
| `EXCHANGE`    | -           | **YES**       | see below                                                                                                              |
| `API_KEY`     | -           | NO            | set this to your Exchange API key                                                                                      |
| `API_SECRET`  | -           | NO            | set this to your Exchange API secret                                                                                   |
| `API_SECRET`  | -           | NO            | only needed for certain exchanges (like `cex`)                                                                         |
| `LOGLEVEL`    | `INFO`      | NO            | [Logging Level](https://docs.python.org/3/library/logging.html#levels)                                                 |
| `GELF_HOST`   | -           | NO            | if set, the exporter will also log to this [GELF](https://docs.graylog.org/en/3.0/pages/gelf.html) capable host on UDP |
| `GELF_PORT`   | `12201`     | NO            | Ignored, if `GELF_HOST` is unset. The UDP port for GELF logging                                                        |
| `PORT`        | `9188`      | NO            | The port for prometheus metrics                                                                                        |

### Supported (tested) exchanges
* poloniex
* kraken
* binance
* bitfinex
* bitstamp
* cex
* hitbtc
* liquid
* gdax

All other exchanges supported by [ccxt](https://github.com/ccxt/ccxt) should be supported, however they are untested.

## Resources:
* GitLab: https://gitlab.com/ix.ai/crypto-exporter
* Docker Hub: https://hub.docker.com/r/ixdotai/crypto-exporter
