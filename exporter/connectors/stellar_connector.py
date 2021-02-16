#!/usr/bin/env python3
""" Handles the stellar data and communication """
import logging
from stellar_sdk.server import Server
from ..lib import utils
from .connector import Connector

log = logging.getLogger('crypto-exporter')


class StellarConnector(Connector):
    """ The StellarConnector class """
    settings = {}
    params = {
        'addresses': {
            'key_type': 'list',
            'default': None,
            'mandatory': True,
        },
        'url': {
            'key_type': 'string',
            'default': 'https://horizon.stellar.org/',
            'mandatory': False,
        },
    }

    def __init__(self):
        self.exchange = 'stellar'
        self.params.update(super().params)  # merge with the global params
        self.settings = utils.gather_environ(self.params)
        self.server = Server(horizon_url=self.settings['url'])
        super().__init__()

    def retrieve_accounts(self):
        """ Connects to the Stellar network and retrieves the account information """
        log.info('Retrieving accounts')
        for account in self.settings['addresses']:
            balances = self.server.accounts().account_id(account).call().get('balances')
            if isinstance(balances, list):
                for balance in balances:
                    if balance.get('asset_code'):
                        currency = balance.get('asset_code')
                    elif balance.get('asset_type') == 'native':
                        currency = 'XLM'
                    else:
                        currency = balance.get('asset_type')
                    if currency not in self._accounts:
                        self._accounts.update({currency: {}})
                    self._accounts[currency].update({
                        f'{account}': float(balance.get('balance'))
                    })

        log.log(5, f'Found the following accounts: {self._accounts}')
