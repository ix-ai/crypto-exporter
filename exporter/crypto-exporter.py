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
from .lib import utils
from .lib import errors

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
    options = utils.gather_environ(params)
    exchange = os.environ.get('EXCHANGE', 'unconfigured')
    log = logging.setup_logger(
        name='crypto-exporter',
        level=options['loglevel'],
        gelf_host=options['gelf_host'],
        gelf_port=options['gelf_port'],
        _exchange=exchange,
        _ix_id=f'{__package__}-{exchange}',
        _version=version,
    )

    try:
        if exchange == 'unconfigured':
            raise ValueError("Missing EXCHANGE environment variable. See README.md.")
    except ValueError as e:
        log.error(f'{e}')
        sys.exit()

    try:
        if exchange == 'etherscan':
            from .connectors.etherscan_connector import EtherscanConnector
            connector = EtherscanConnector()
        elif exchange == 'ethplorer':
            from .connectors.ethplorer_connector import EthplorerConnector
            connector = EthplorerConnector()
        elif exchange == 'blockscout':
            from .connectors.blockscout_connector import BlockscoutConnector
            connector = BlockscoutConnector()
        elif exchange == 'blockchain':
            from .connectors.blockchain_connector import BlockchainConnector
            connector = BlockchainConnector()
        elif exchange == 'ripple':
            from .connectors.ripple_connector import RippleConnector
            connector = RippleConnector()
        elif exchange == 'stellar':
            from .connectors.stellar_connector import StellarConnector
            connector = StellarConnector()
        else:
            from .connectors.ccxt_connector import CcxtConnector
            connector = CcxtConnector(exchange=exchange)
    except errors.EnvironmentMissing as e:
        log.error(f'{e}')
        sys.exit()

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
