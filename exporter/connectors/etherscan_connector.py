#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Handles the etherscan data and communication """

import logging
import time
import requests
from ..lib import utils
from .connector import Connector

log = logging.getLogger('crypto-exporter')


class EtherscanConnector(Connector):
    """
    The EtherscanConnector class

    Originally written for the ix.ai/etherscan-exporter, this class is in dire need of refactoring
    """

    settings = {}
    params = {
        'api_key': {
            'key_type': 'string',
            'default': None,
            'mandatory': True,
            'redact': True,
        },
        'addresses': {
            'key_type': 'list',
            'default': None,
            'mandatory': True,
        },
        'tokens': {
            'key_type': 'json',
            'default': None,
            'mandatory': False,
        },
        'url': {
            'key_type': 'string',
            'default': 'https://api.etherscan.io/api',
            'mandatory': False,
        },
    }

    def __init__(self, **kwargs):
        self.exchange = 'etherscan'
        self.settings = {
            'api_key': kwargs.get('api_key'),
            'url': kwargs.get("url", self.params['url']['default']),
            'addresses': kwargs.get('addresses', self.params['addresses']['default']),
            'tokens': kwargs.get('tokens', self.params['tokens']['default']),
            'enable_authentication': True
        }

        if not self.settings.get('api_key'):
            raise ValueError("Missing api_key")

    def _get_tokens(self):
        """ Gets the tokens from an account """
        log.info('Retrieving the tokens')
        for account in self._accounts['ETH']:
            for token in self.settings['tokens']:
                log.debug(f"Retrieving the balance for {token['short']} on the account {account}")
                request_data = {
                    'module': 'account',
                    'action': 'tokenbalance',
                    'contractaddress': token['contract'],
                    'address': account,
                    'tag': 'latest',
                    'apikey': self.settings['api_key'],
                }
                decimals = 18
                if token.get('decimals', -1) >= 0:
                    decimals = int(token['decimals'])
                try:
                    req = requests.get(self.settings['url'], params=request_data).json()
                except (
                        requests.exceptions.ConnectionError,
                        requests.exceptions.ReadTimeout,
                ) as error:
                    log.exception(f'Exception caught: {utils.short_msg(error)}')
                    req = {}
                if req.get('result') and int(req['result']) > 0:
                    if not self._accounts.get(token['short']):
                        self._accounts.update({
                            token['short']: {}
                        })
                    self._accounts[token['short']].update({
                        account: int(req['result']) / (10**decimals) if decimals > 0 else int(req['result'])
                    })
                time.sleep(1)  # Ensure that we don't get rate limited

    def retrieve_accounts(self):
        """ Gets the current balance for an account """
        if self.settings['enable_authentication']:
            log.info('Retrieving the account balances')
            request_data = {
                'module': 'account',
                'action': 'balancemulti',
                'address': self.settings['addresses'],
                'tag': 'latest',
                'apikey': self.settings['api_key'],
            }
            try:
                req = requests.get(self.settings['url'], params=request_data).json()
            except (
                    requests.exceptions.ConnectionError,
                    requests.exceptions.ReadTimeout,
            ) as error:
                log.exception(f'Exception caught: {utils.short_msg(error)}')
                req = {}
            log.debug(req)
            if req.get('message') == 'OK' and req.get('result'):
                if not self._accounts.get('ETH'):
                    self._accounts.update({'ETH': {}})
                for result in req.get('result'):
                    self._accounts['ETH'].update({
                        result['account']: float(result['balance'])/(1000000000000000000)
                    })
            if req.get('message') == 'NOTOK' and req.get('result') == 'Invalid API Key':
                utils.AuthenticationErrorHandler(req.get('result'))
                self.settings['enable_authentication'] = False

            if self.settings['tokens']:
                self._get_tokens()
        log.debug(f'Accounts: {self._accounts}')
        return self._accounts
