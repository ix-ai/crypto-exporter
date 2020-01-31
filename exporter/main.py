#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Prometheus Exporter for Crypto Exchanges """

import logging
import time
import os
import sys
import pygelf
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY
from .crypto_collector import CryptoCollector
from .exchange import Exchange
from .lib import constants

logging.basicConfig(
    stream=sys.stdout,
    level=os.environ.get("LOGLEVEL", "WARNING"),
    format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger(__name__)


def main():
    """ The main function """

    GELF_ENABLED = False
    if os.environ.get('GELF_HOST') and not GELF_ENABLED:
        GELF = pygelf.GelfUdpHandler(
            host=os.environ.get('GELF_HOST'),
            port=int(os.environ.get('GELF_PORT', 12201)),
            debug=True,
            include_extra_fields=True,
            _exchange=os.environ.get('EXCHANGE', 'unconfigured'),
            _ix_id=os.environ.get('EXCHANGE', os.path.splitext(sys.modules['__main__'].__file__)[0]),
        )
        log.addHandler(GELF)
        GELF_ENABLED = True
        log.info('GELF logging enabled')

    PORT = int(os.environ.get('PORT', 9188))
    log.warning("Starting {} {}-{} on port {}".format(__package__, constants.VERSION, constants.BUILD, PORT))

    options = {}

    options['exchange'] = os.environ.get('EXCHANGE')
    if not options['exchange']:
        raise ValueError("Missing EXCHANGE environment variable. See README.md.")
    log.info('Configured EXCHANGE: {}'.format(options['exchange']))

    options['nonce'] = os.environ.get('NONCE', 'milliseconds')
    log.info('Configured NONCE: {}'.format(options['nonce']))

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

    exchange = Exchange(**options)

    collector = CryptoCollector(exchange=exchange)

    REGISTRY.register(collector)

    start_http_server(PORT)
    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
