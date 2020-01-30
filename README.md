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

**Warning**: some exchanges (notably: coinbasepro) need more than 30s to scrape

### Supported variables
| **Variable**             | **Default**    | **Mandatory** | **Description**  |
|:-------------------------|:--------------:|:-------------:|:-----------------|
| `EXCHANGE`               | -              | **YES**       | See below [Tested exchanges](#tested-exchanges) |
| `API_KEY`                | -              | NO            | Set this to your Exchange API key |
| `API_SECRET`             | -              | NO            | Set this to your Exchange API secret |
| `API_PASS`               | -              | NO            | Only needed for certain exchanges (like `coinbasepro`) |
| `API_UID`                | -              | NO            | Only needed for certain exchanges (like `cex`) |
| `NONCE`                  | `milliseconds` | NO            | Some exchanges (looking at you, `coinbasepro`) don't support nonce in milliseconds, but want seconds |
| `ENABLE_TICKERS`         | `true`         | NO            | Set this to anything else in order to disable retrieving the ticker rates |
| `SYMBOLS`                | -              | NO            | See below for explanation ([SYMBOLS and REFERENCE_CURRENCIES](#symbols-and-referece_currencies)) |
| `REFERENCE_CURRENCIES`   | -              | NO            | See below for explanation ([SYMBOLS and REFERENCE_CURRENCIES](#symbols-and-referece_currencies)) |
| `LOGLEVEL`               | `WARNING`      | NO            | [Logging Level](https://docs.python.org/3/library/logging.html#levels) |
| `GELF_HOST`              | -              | NO            | If set, the exporter will also log to this [GELF](https://docs.graylog.org/en/3.0/pages/gelf.html) capable host on UDP |
| `GELF_PORT`              | `12201`        | NO            | Ignored, if `GELF_HOST` is unset. The UDP port for GELF logging |
| `PORT`                   | `9188`         | NO            | The port for prometheus metrics |

### SYMBOLS and REFERENCE_CURRENCIES

Since not all exchanges support getting the ticker with one request (`coinbase`, `coinbasepro`, `bitstamp`), crypto-exporter has to request for every traded pair the exchange rate. This takes a lot of time, especially if there are a lot of pairs traded (>50 minutes for one run with coinbase).

If you're only interested in a subset of those trade pairs, you can:

* set `REFERENCE_CURRENCIES` to a comma separated list of currencies, for which to retrieve all exchange rates (for example: `EUR,USD`)
* set `SYMBOLS` to a comma separated list of pairs (for example: `BTC/EUR,BTC/USD,ETH/EUR,ETH/USD`) and all the other pairs will be ignored

The two variables are *cumulative*. If you set both, for example `REFERENCE_CURRENCIES=EUR` and `SYMBOLS=BTC/USDT`, you will get the results for all trading pairs for EUR and BTC/USDT.

### Tested exchanges
* coinbase
* coinbasepro
* kraken
* binance
* liquid
* poloniex
* bitfinex
* cex

Limited tests (without API credentials) have been done with:
* bitstamp
* hitbtc

All other exchanges supported by [ccxt](https://github.com/ccxt/ccxt) should be work as well, however they are untested.

## Tags and Arch

Starting with version v0.5.1, the images are multi-arch, with builds for amd64, arm64, armv7 and armv6.
* `vN.N.N` - for example v0.5.0
* `latest` - always pointing to the latest version
* `dev-master` - the last build on the master branch

## Resources:
* GitLab: https://gitlab.com/ix.ai/crypto-exporter
* GitHub: https://github.com/ix-ai/crypto-exporter
* Docker Hub: https://hub.docker.com/r/ixdotai/crypto-exporter
