#!/usr/bin/env python3
""" Handles the ripple data and communication """

import logging
import time
import requests
from ..lib import utils
from .connector import Connector

log = logging.getLogger('crypto-exporter')


class RippleConnector(Connector):
    """ The RippleConnector class """
    settings = {}
    params = {
        'addresses': {
            'key_type': 'list',
            'default': None,
            'mandatory': True,
        },
        'url': {
            'key_type': 'string',
            'default': 'https://data.ripple.com',
            'mandatory': False,
        },
    }

    def __init__(self):
        self.exchange = 'ripple'
        self.params.update(super().params)  # merge with the global params
        self.settings = utils.gather_environ(self.params)
        super().__init__()

    def retrieve_accounts(self):
        """ Connects to the ripple API and retrieves the account information """
        if not self.settings['addresses']:
            return
        for account in self.settings['addresses']:
            url = f"{self.settings['url']}/v2/accounts/{account}/balances"
            r = {}
            try:
                r = requests.get(url, timeout=self.settings['timeout']).json()
            except (
                    requests.exceptions.ConnectionError,
                    requests.exceptions.ReadTimeout,
            ) as e:
                log.warning(f"Can't connect to {self.settings['url']}. Exception caught: {utils.short_msg(e)}")

            if r.get('result') == 'success' and r.get('balances'):
                for balance in r.get('balances'):
                    value = float(balance.get('value'))
                    currency = balance.get('currency')
                    if currency not in self._accounts:
                        self._accounts.update({currency: {}})
                    self._accounts[currency].update({
                        account: value,
                    })

            time.sleep(1)  # Don't hit the rate limit
        log.log(5, f"Found the following accounts: {self._accounts}")
