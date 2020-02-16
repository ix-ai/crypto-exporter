#!/usr/bin/env sh
set -ex

./build.sh

for EXCHANGE in "kraken" "binance" "coinbasepro"; do
  LOGLEVEL=DEBUG EXCHANGE="${EXCHANGE}" REFERENCE_CURRENCY="EUR" SYMBOLS="BTC/EUR" TEST=y ./crypto-exporter.sh
done
