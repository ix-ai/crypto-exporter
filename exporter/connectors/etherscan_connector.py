#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Handles the etherscan data and communication """

import logging
import requests
from ..lib import utils
from .connector import Connector

log = logging.getLogger('crypto-exporter')


class EtherscanConnector(Connector):
    """ The EtherscanConnector class """

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

    def __init__(self):
        self.exchange = 'etherscan'
        self.params.update(super().params)  # merge with the global params
        self.settings = utils.gather_environ(self.params)
        self.settings.update({'enable_authentication': True})
        super().__init__()

    def __load_retry(self, request_data: dict, retries=5):
        """ Tries up to {retries} times to call the ccxt function and then gives up """
        data = None
        retry = True
        result = None
        count = 0
        log.debug(f'Loading {request_data} with {retries} retries')
        while retry:
            try:
                count += 1
                if count > retries:
                    log.warning('Maximum number of retries reached. Giving up.')
                    message = self.redact(f'{request_data}')
                    log.debug(f'Reached max retries while loading {message}')
                else:
                    request_data.update({
                        'apikey': self.settings['api_key'],
                        'module': 'account',
                        'tag': 'latest',
                    })
                    req = requests.get(self.settings['url'], params=request_data, timeout=self.settings['timeout'])
                    req.raise_for_status()
                    data = req.json()
                retry = False
            except requests.exceptions.Timeout as e:
                error = self.redact(str(e))
                utils.exchange_not_available_handler(error=error, shortify=False, sleep=2)
            except requests.exceptions.RequestException as e:
                error = self.redact(str(e))
                log.warning(f"Fatal error connecting to {self.settings['url']}. Exception caught: {error}")
                retry = False

            if data:
                if (data.get('message') == 'OK' or 'OK-' in data.get('message')) and data.get('result'):
                    result = data.get('result')

                if 'NOTOK' in data.get('message'):
                    retry = False
                    if data.get('result') == 'Invalid API Key':
                        utils.authentication_error_handler(self.redact(data.get('result')))
                        self.settings['enable_authentication'] = False
                    else:
                        utils.generic_error_handler(self.redact(data.get('result')))

        return result

    def _get_token_balance_on_account(self, account: str, token: dict) -> float:
        """
        gets a specific token on a specific account
        :param account The Etherium account
        :param token The token details containing `contract`, `decimals`, `short`
        :return the balance
        """
        request_data = {
            'action': 'tokenbalance',
            'contractaddress': token['contract'],
            'address': account,
        }

        balance = 0
        data = self.__load_retry(request_data)
        if data and int(data) > 0:
            decimals = 18
            if token.get('decimals', -1) >= 0:
                decimals = int(token['decimals'])
            balance = int(data) / (10**decimals) if decimals > 0 else int(data)
        return float(balance)

    def retrieve_tokens(self):
        """ Gets the tokens from an account """
        log.debug('Retrieving the tokens')
        if not self._accounts.get('ETH'):
            self._accounts.update({'ETH': {}})
        for account in self._accounts['ETH']:
            for token in self.settings['tokens']:
                if not self._accounts.get(token['short']):
                    self._accounts.update({
                        token['short']: {}
                    })
                self._accounts[token['short']].update({
                    account: self._get_token_balance_on_account(account, token)
                })

    def retrieve_accounts(self):
        """ Gets the current balance for an account """
        if self.settings['enable_authentication']:
            log.debug('Retrieving the account balances')
            request_data = {
                'action': 'balancemulti',
                'address': self.settings['addresses'],
            }
            data = self.__load_retry(request_data)
            if data:
                if not self._accounts.get('ETH'):
                    self._accounts.update({'ETH': {}})
                for account in data:
                    self._accounts['ETH'].update({
                        account['account']: float(account['balance'])/(1000000000000000000)
                    })
            if self.settings['tokens']:
                self.retrieve_tokens()
        log.log(5, f'Accounts: {self._accounts}')
        return self._accounts
