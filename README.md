# crypto-exporter
Prometheus exporter, written in python, for different exchanges

## Usage
```
docker run --rm -it -p 9308:9308 \
  -e LOGLEVEL=DEBUG \
  -e API_KEY="your_api_key" \
  -e API_SECRET="your_api_secret" \
  -e EXPORTER="poloniex" \
  --name poloniex-exporter \
  hub.ix.ai/docker/crypto-exporter:latest
```

### Supported variables
* `EXCHANGE` (no default - **mandatory**) - see below
* `API_KEY` (no default) - set this to your Exchange API key
* `API_SECRET` (no default) - set this to your Exchange API secret
* `API_UID` (no default) - only needed for certain exchanges (like `cex`)
* `GELF_HOST` (no default) - if set, the exporter will also log to this [GELF](https://docs.graylog.org/en/3.0/pages/gelf.html) capable host on UDP
* `GELF_PORT` (defaults to `12201`) - the port to use for GELF logging
* `PORT` (defaults to `9308`) - the listen port for the exporter
* `LOGLEVEL` (defaults to `INFO`)

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
