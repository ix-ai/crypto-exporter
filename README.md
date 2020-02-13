# crypto-exporter

[![Pipeline Status](https://gitlab.com/ix.ai/crypto-exporter/badges/master/pipeline.svg)](https://gitlab.com/ix.ai/crypto-exporter/)
[![Docker Stars](https://img.shields.io/docker/stars/ixdotai/crypto-exporter.svg)](https://hub.docker.com/r/ixdotai/crypto-exporter/)
[![Docker Pulls](https://img.shields.io/docker/pulls/ixdotai/crypto-exporter.svg)](https://hub.docker.com/r/ixdotai/crypto-exporter/)
[![Gitlab Project](https://img.shields.io/badge/GitLab-Project-554488.svg)](https://gitlab.com/ix.ai/crypto-exporter/)

Prometheus exporter, written in python, for different crypto exchanges

**Warning**: This documentation applies for version `v1.x.x`.

## Features

The crypto-exporter generates two sets of metrics:

### exchange_rate
The exchange rates for the symbols traded. Use this to get the tickers.

Example:
```prom
# HELP exchange_rate Current exchange rates
# TYPE exchange_rate gauge
exchange_rate{currency="BTC",exchange="bitfinex",reference_currency="USD"} 9386.9
exchange_rate{currency="LTC",exchange="bitfinex",reference_currency="USD"} 70.256
exchange_rate{currency="LTC",exchange="bitfinex",reference_currency="BTC"} 0.007498
exchange_rate{currency="ETH",exchange="bitfinex",reference_currency="USD"} 182.59
exchange_rate{currency="ETH",exchange="bitfinex",reference_currency="BTC"} 0.019445
exchange_rate{currency="ETC",exchange="bitfinex",reference_currency="BTC"} 0.0012486
exchange_rate{currency="ETC",exchange="bitfinex",reference_currency="USD"} 11.712
exchange_rate{currency="RRT",exchange="bitfinex",reference_currency="USD"} 0.0234
```

### Account balance
**Warning**: To see the account balance, authentication is mandatory.

Example:
```prom
# HELP account_balance Account Balance
# TYPE account_balance gauge
account_balance{account="total",currency="XRP",exchange="kraken"} 279.39357642
account_balance{account="total",currency="XLM",exchange="kraken"} 14.0003552
account_balance{account="total",currency="ETH",exchange="kraken"} 9.29332537
```

### Transaction totals
**Warning** To see the totals, authentication is mandatory.

Example:
```prom
# HELP transactions_total The transaction history for an account
# TYPE transactions_total gauge
transactions_total{currency="XLM",exchange="coinbase",reference_currency="EUR",type="trade"} -60.0
transactions_total{currency="XRP",exchange="coinbase",reference_currency="EUR",type="trade"} -50.0
transactions_total{currency="LTC",exchange="coinbase",reference_currency="EUR",type="trade"} -108.18
transactions_total{currency="ETH",exchange="coinbase",reference_currency="EUR",type="trade"} 149.5100000000007
transactions_total{currency="BTC",exchange="coinbase",reference_currency="EUR",type="trade"} -1639.779999999999
```

See also [ENABLE_TRANSACTIONS](#enable_transactions)

## Usage
```sh
docker run --rm -it -p 9999:9999 \
  -e EXCHANGE="coinbasepro" \
  -e NONCE="seconds" \
  -e API_KEY="your_api_key" \
  -e API_SECRET="your_api_secret" \
  -e API_PASS="your_api_password" \
  -e REFERENCE_CURRENCIES="USD,EUR" \
  -e SYMBOLS="LTC/BTC,ETH/BTC" \
  -e GELF_HOST="graylog" \
  -e GELF_PORT="2201" \
  -e LOGLEVEL=DEBUG \
  -e PORT=9999 \
  --name coinbasepro-exporter \
  ixdotai/crypto-exporter:latest
```

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
| `ENABLE_TRANSACTIONS`    | `false`        | NO            | Set this to `true` in order to enable retrieving the transaction totals. See also below [ENABLE_TRANSACTIONS](#enable-transactions) |
| `SYMBOLS`                | -              | NO            | See below for explanation ([SYMBOLS and REFERENCE_CURRENCIES](#symbols-and-referece_currencies)) |
| `REFERENCE_CURRENCIES`   | -              | NO            | See below for explanation ([SYMBOLS and REFERENCE_CURRENCIES](#symbols-and-referece_currencies)) |
| `LOGLEVEL`               | `INFO`         | NO            | [Logging Level](https://docs.python.org/3/library/logging.html#levels) |
| `GELF_HOST`              | -              | NO            | If set, the exporter will also log to this [GELF](https://docs.graylog.org/en/3.0/pages/gelf.html) capable host on UDP |
| `GELF_PORT`              | `12201`        | NO            | Ignored, if `GELF_HOST` is unset. The UDP port for GELF logging |
| `PORT`                   | `9188`         | NO            | The port for prometheus metrics |

### SYMBOLS and REFERENCE_CURRENCIES

Since not all exchanges support getting the ticker with one request (`coinbase`, `coinbasepro`, `bitstamp`), crypto-exporter has to request for every traded pair the exchange rate. This takes a lot of time, especially if there are a lot of pairs traded (>50 minutes for one run with coinbase).

If you're only interested in a subset of those trade pairs, you can:

* set `REFERENCE_CURRENCIES` to a comma separated list of currencies, for which to retrieve all exchange rates (for example: `EUR,USD`)
* set `SYMBOLS` to a comma separated list of pairs (for example: `BTC/EUR,BTC/USD,ETH/EUR,ETH/USD`) and all the other pairs will be ignored

The two variables are *cumulative*. If you set both, for example `REFERENCE_CURRENCIES=EUR` and `SYMBOLS=BTC/USDT`, you will get the results for all trading pairs for EUR and BTC/USDT.

### ENABLE_TRANSACTIONS

**Note** This metric is gathered for all the individual accounts that are found. If the exchange created a lot of currency accounts for you, it will take a while to query all

This metric can be interpreted as follows (from the [example above](#transaction-totals)):

```prom
transactions_total{currency="XRP",exchange="coinbase",reference_currency="EUR",type="trade"} -50.0
transactions_total{currency="ETH",exchange="coinbase",reference_currency="EUR",type="trade"} 149.5100000000007
transactions_total{currency="EUR",exchange="kraken",reference_currency="XLM",type="trade"} -596.117
transactions_total{currency="XLM",exchange="kraken",reference_currency="EUR",type="trade"} 69.14959999999999
```
* When looking at the sum of all XRP/EUR transactions, `-50` EUR profit was made. So, more Euros were lost by buying XRP than were made by selling
* When looking at the sum of all ETH/EUR transactions, `149.51` EUR profit were made. So, more Euros were gained by selling ETH than were made by buying

This option is disabled by default, since there aren't many exchanges that support it and it increases the time, by querying the exchange. So far, it has been tested successfully with `coinbase` and `kraken`.

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

All other exchanges supported by [ccxt](https://github.com/ccxt/ccxt) should work as well, however they are untested.

## docker-compose or stack example
```yml
version: '3.7'

services:
  binance:
    image: ixdotai/crypto-exporter:latest
    networks:
      - exporters
    environment:
      EXCHANGE: binance
      API_KEY: your_api_key
      API_SECRET: your_api_secret
      LOGLEVEL: DEBUG
  bitfinex:
    image: registry.gitlab.com/ix.ai/crypto-exporter:latest
    networks:
      - exporters
    environment:
      EXCHANGE: bitfinex
      API_KEY: your_api_key
      API_SECRET: your_api_secret
      LOGLEVEL: WARNING
  coinbasepro:
    image: ixdotai/crypto-exporter:v1.0.0
    networks:
      - exporters
    environment:
      EXCHANGE: coinbasepro
      REFERENCE_CURRENCIES: USD,EUR,BTC
      SYMBOLS: LTC/BTC,ETH/BTC
      NONCE: seconds
networks:
  exporters: {}
```

Prometheus configuration with DNS service discovery:

```yml
scrape_configs:
- job_name: 'crypto-exporters'
  scrape_interval: 60s
  scrape_timeout: 60s
  metrics_path: /
  scheme: http
  dns_sd_configs:
  - port: 9188
  - names:
    - tasks.binance
    - tasks.bitfinex
- job_name: 'coinbasepro-exporter'
  scrape_interval: 120s
  scrape_timeout: 120s
  metrics_path: /
  dns_sd_configs:
  - port: 9188
  - names:
    - tasks.coinbasepro
```

Make sure that your prometheus server is able to reach the network set for the crypto-exporter.

**Warning**: Some exchanges (notably: coinbasepro) need more than 60s to scrape, especially if you don't configure `REFERENCE_CURRENCIES` or `SYMBOLS`.

## Tags and Arch

Starting with version v0.5.1, the images are multi-arch, with builds for amd64, arm64, armv7 and armv6.
* `vN.N.N` - for example v0.5.0
* `latest` - always pointing to the latest version
* `dev-master` - the last build on the master branch

## Resources:
* GitLab: https://gitlab.com/ix.ai/crypto-exporter
* GitHub: https://github.com/ix-ai/crypto-exporter
* Docker Hub: https://hub.docker.com/r/ixdotai/crypto-exporter
