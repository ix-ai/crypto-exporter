#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Prometheus Exporter for Crypto Exchanges """

import time
import os
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY
from .crypto_collector import CryptoCollector
from .exchange import Exchange
from .lib import constants
from .lib.log import ExporterLogging

log = ExporterLogging()


def main():
    """ The main function """
    # log.configure_logging()
    PORT = int(os.environ.get('PORT', 9188))
    log.LOG.info("Starting {} {}-{} on port {}".format(__package__, constants.VERSION, constants.BUILD, PORT))

    options = {}

    options['exchange'] = os.environ.get('EXCHANGE')
    if not options['exchange']:
        raise ValueError("Missing EXCHANGE environment variable. See README.md.")
    log.LOG.info('Configured EXCHANGE: {}'.format(options['exchange']))

    options['nonce'] = os.environ.get('NONCE', 'milliseconds')
    log.LOG.info('Configured NONCE: {}'.format(options['nonce']))

    if os.environ.get("API_KEY"):
        options['api_key'] = os.environ.get('API_KEY')
        log.LOG.info('Configured API_KEY')
    if os.environ.get("API_SECRET"):
        options['api_secret'] = os.environ.get('API_SECRET')
        log.LOG.info('Configured API_SECRET')
    if os.environ.get("API_UID"):
        options['api_key'] = os.environ.get('API_UID')
        log.LOG.info('Configured API_UID')
    if os.environ.get("API_PASS"):
        options['api_secret'] = os.environ.get('API_PASS')
        log.LOG.info('Configured API_PASS')

    options['enable_tickers'] = False
    if os.environ.get('ENABLE_TICKERS', 'true') == 'true':
        options['enable_tickers'] = True
    log.LOG.info('Configured ENABLE_TICKERS: {}'.format(options['enable_tickers']))

    if os.environ.get("SYMBOLS"):
        options['symbols'] = os.environ.get("SYMBOLS")
        log.LOG.info('Configured SYMBOLS: {}'.format(options['symbols']))
    if os.environ.get("REFERENCE_CURRENCIES"):
        options['reference_currencies'] = os.environ.get("REFERENCE_CURRENCIES")
        log.LOG.info('Configured REFERENCE_CURRENCIES: {}'.format(options['reference_currencies']))

    exchange = Exchange(**options)

    collector = CryptoCollector(exchange=exchange)

    REGISTRY.register(collector)

    start_http_server(PORT)
    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
