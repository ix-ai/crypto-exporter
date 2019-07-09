# poloniex-exporter
Prometheus exporter, written in python, for Poloniex

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
* `API_KEY` (no default) - set this to your Exchange API key
* `API_SECRET` (no default) - set this to your Exchange API secret
* `API_UID` (no default) - only neeeded for certain exchanges (like cex)
* `EXCHANGE` (no default) - see below
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
