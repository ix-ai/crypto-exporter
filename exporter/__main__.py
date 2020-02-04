#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Prometheus Exporter for Crypto Exchanges """

import time
import os
import sys
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY
from .crypto_collector import CryptoCollector
from .exchange import Exchange
from .lib import constants
from .lib import log as logging

log = logging.setup_logger(
    name='crypto-exporter',
    level=os.environ.get('LOGLEVEL', 'INFO'),
    gelf_host=os.environ.get('GELF_HOST'),
    gelf_port=int(os.environ.get('GELF_PORT', 12201)),
    _exchange=os.environ.get('EXCHANGE', 'unconfigured'),
    _ix_id=os.environ.get('EXCHANGE', os.path.splitext(sys.modules['__main__'].__file__)[0]),
)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9188))
    log.warning("Starting {} {}-{} on port {}".format(__package__, constants.VERSION, constants.BUILD, port))
    log.warning("The labels 'source_currency' and 'target_currency' are deprecated and will likely be removed soon")
    options = {}

    options['exchange'] = os.environ.get('EXCHANGE')
    if not options['exchange']:
        raise ValueError("Missing EXCHANGE environment variable. See README.md.")
    log.info('Configured EXCHANGE: {}'.format(options['exchange']))

    if os.environ.get("API_KEY"):
        options['api_key'] = os.environ.get('API_KEY')
        log.info('Configured API_KEY')
    if os.environ.get("API_SECRET"):
        options['api_secret'] = os.environ.get('API_SECRET')
        log.info('Configured API_SECRET')
    if os.environ.get("API_UID"):
        options['api_uid'] = os.environ.get('API_UID')
        log.info('Configured API_UID')
    if os.environ.get("API_PASS"):
        options['api_pass'] = os.environ.get('API_PASS')
        log.info('Configured API_PASS')

    options['enable_tickers'] = False
    if os.environ.get('ENABLE_TICKERS', 'true').lower() == 'true':
        options['enable_tickers'] = True
    log.info('Configured ENABLE_TICKERS: {}'.format(options['enable_tickers']))

    if os.environ.get("SYMBOLS"):
        options['symbols'] = os.environ.get("SYMBOLS")
        log.info('Configured SYMBOLS: {}'.format(options['symbols']))
    if os.environ.get("REFERENCE_CURRENCIES"):
        options['reference_currencies'] = os.environ.get("REFERENCE_CURRENCIES")
        log.info('Configured REFERENCE_CURRENCIES: {}'.format(options['reference_currencies']))

    options['nonce'] = os.environ.get('NONCE', 'milliseconds')
    log.info('Configured NONCE: {}'.format(options['nonce']))

    log.info('Configured LOGLEVEL: {}'.format(os.environ.get('LOGLEVEL', 'INFO')))
    if os.environ.get('GELF_HOST'):
        log.info('Configured GELF_HOST: {}'.format(os.environ.get('GELF_HOST')))
        log.info('Configured GELF_PORT: {}'.format(int(os.environ.get('GELF_PORT', 12201))))

    exchange = Exchange(**options)

    collector = CryptoCollector(exchange=exchange)

    REGISTRY.register(collector)

    start_http_server(port)
    while True:
        time.sleep(1)
