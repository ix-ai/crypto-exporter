# docker-compose Example

```yml
version: '3.7'

services:
  binance:
    image: registry.gitlab.com/ix.ai/crypto-exporter:latest
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
    image: registry.gitlab.com/ix.ai/crypto-exporter:v1.0.0
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
