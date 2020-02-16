#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Prometheus Exporter for Crypto Exchanges """

import time
import os
import sys
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY
from .crypto_collector import CryptoCollector
from .lib import log as logging
from .lib import constants
from .lib.utils import gather_environ

version = f'{constants.VERSION}-{constants.BUILD}'

if __name__ == '__main__':
    # The generic params - always active
    params = {
        'port': {
            'key_type': 'int',
            'default': 9188,
            'mandatory': False,
        },
        'loglevel': {
            'key_type': 'string',
            'default': 'INFO',
            'mandatory': False,
        },
        'gelf_host': {
            'key_type': 'string',
            'default': None,
            'mandatory': False,
        },
        'gelf_port': {
            'key_type': 'int',
            'default': '12201',
            'mandatory': False,
        }
    }
    options = gather_environ(params)
    exchange = os.environ.get('EXCHANGE', 'unconfigured')
    log = logging.setup_logger(
        name='crypto-exporter',
        level=options['loglevel'],
        gelf_host=options['gelf_host'],
        gelf_port=options['gelf_port'],
        _exchange=exchange,
        _ix_id=__package__,
        _version=version,
    )

    try:
        if exchange == 'unconfigured':
            raise ValueError("Missing EXCHANGE environment variable. See README.md.")
    except ValueError as e:
        log.error(f'{e}')
        sys.exit()

    if exchange == 'etherscan':
        from .connectors.etherscan_connector import EtherscanConnector
        try:
            options.update(gather_environ(EtherscanConnector.params))
        except KeyError as e:
            log.error(f'{e}')
            sys.exit()
        connector = EtherscanConnector(**options)
    elif exchange == 'blockchain':
        from .connectors.blockchain_connector import BlockchainConnector
        try:
            options.update(gather_environ(BlockchainConnector.params))
        except KeyError as e:
            log.error(f'{e}')
            sys.exit()
        connector = BlockchainConnector(**options)
    else:
        from .connectors.ccxt_connector import CcxtConnector
        try:
            options.update(gather_environ(CcxtConnector.params))
        except KeyError as e:
            log.error(f'{e}')
            sys.exit()
        connector = CcxtConnector(exchange=exchange, **options)

    log.info(f"Starting {__package__} {version} on port {options['port']}")

    if os.environ.get('TEST'):
        log.warning('Running in TEST mode')
        collector = CryptoCollector(exchange=connector)
        for metric in collector.collect():
            log.info(f"{metric}")
    else:
        collector = CryptoCollector(exchange=connector)
        REGISTRY.register(collector)
        start_http_server(options['port'])
        while True:
            time.sleep(1)
