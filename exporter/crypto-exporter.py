#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Prometheus Exporter for Crypto Exchanges """

import logging
import time
import os
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY
from .crypto_collector import CryptoCollector
from .lib import constants

log = logging.getLogger(__package__)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9188))
    log.warning(f'Starting {__package__} {constants.VERSION}-{constants.BUILD} on port {port}')
    options = {}

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
    log.info(f"Configured ENABLE_TICKERS: {options['enable_tickers']}")

    options['enable_transactions'] = False
    if os.environ.get('ENABLE_TRANSACTIONS', 'false').lower() == 'true':
        options['enable_transactions'] = True
        log.info(f"Configured ENABLE_TRANSACTIONS: {options['enable_transactions']}")

    options['enable_zero_balance'] = False
    if os.environ.get('ENABLE_ZERO_BALANCE', 'false').lower() == 'true':
        options['enable_zero_balance'] = True
        log.info(f"Configured ENABLE_ZERO_BALANCE: {options['enable_zero_balance']}")

    if os.environ.get("SYMBOLS"):
        options['symbols'] = os.environ.get("SYMBOLS")
        log.info(f"Configured SYMBOLS: {options['symbols']}")
    if os.environ.get("REFERENCE_CURRENCIES"):
        options['reference_currencies'] = os.environ.get("REFERENCE_CURRENCIES")
        log.info(f"Configured REFERENCE_CURRENCIES: {options['reference_currencies']}")
    if os.environ.get("DEFAULT_EXCHANGE_TYPE"):
        options['default_exchange_type'] = os.environ.get("DEFAULT_EXCHANGE_TYPE")
        log.info(f"Configured DEFAULT_EXCHANGE_TYPE: {options['default_exchange_type']}")

    if os.environ.get("URL"):
        options['url'] = os.environ['URL']
        log.info(f"Configured URL: {options['url']}")

    if os.environ.get("ADDRESSES"):
        options['addresses'] = os.environ['ADDRESSES']
        log.info(f"Configured ADDRESSES: {options['addresses']}")

    if os.environ.get("TOKENS"):
        options['tokens'] = os.environ['TOKENS']
        log.info(f"Configured TOKENS: {options['tokens']}")

    options['nonce'] = os.environ.get('NONCE', 'milliseconds')
    log.info(f"Configured NONCE: {options['nonce']}")

    log.info(f"Configured LOGLEVEL: {os.environ.get('LOGLEVEL', 'INFO')}")
    if os.environ.get('GELF_HOST'):
        log.info(f"Configured GELF_HOST: {os.environ.get('GELF_HOST')}")
        log.info(f"Configured GELF_PORT: {int(os.environ.get('GELF_PORT', 12201))}")

    if os.environ.get('TEST'):
        log.warning('Running in TEST mode')
        for exchange in ['kraken', 'bitfinex']:
            options['exchange'] = exchange
            from .connectors.ccxt_connector import CcxtConnector
            collector = CryptoCollector(exchange=CcxtConnector(**options))
            for metric in collector.collect():
                log.info(f"{metric}")
    else:
        options['exchange'] = os.environ.get('EXCHANGE')
        if not options['exchange']:
            raise ValueError("Missing EXCHANGE environment variable. See README.md.")
        log.info(f"Configured EXCHANGE: {options['exchange']}")

        if options['exchange'] == 'etherscan':
            from .connectors.etherscan_connector import EtherscanConnector
            exchange = EtherscanConnector(**options)
        else:
            from .connectors.ccxt_connector import CcxtConnector
            exchange = CcxtConnector(**options)

        collector = CryptoCollector(exchange=exchange)

        REGISTRY.register(collector)

        start_http_server(port)
        while True:
            time.sleep(1)
