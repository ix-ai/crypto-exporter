#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Handles the blockstout data and communication """

import logging
import requests
from ..lib import utils
from .connector import Connector

log = logging.getLogger('crypto-exporter')


class BlockscoutConnector(Connector):
    """ The BlockscoutConnector class """

    settings = {}
    params = {
        'addresses': {
            'key_type': 'list',
            'default': None,
            'mandatory': True,
        },
        'url': {
            'key_type': 'string',
            'default': 'https://blockscout.com/eth/mainnet/api',
            'mandatory': False,
        },
    }

    def __init__(self):
        self.exchange = 'blockscout'
        self.params.update(super().params)  # merge with the global params
        self.settings = utils.gather_environ(self.params)
        super().__init__()

    def prepare_request(self, request_data: dict) -> dict:
        """ Checks the request_data and adds the missing keys """
        if not request_data.get('module'):
            request_data.update({'module': 'account'})
        if not request_data.get('module'):
            request_data.update({'module': 'account'})
        return request_data

    def __load_retry(self, request_data: dict, retries=5):
        """ Tries up to {retries} times to call the api and then gives up """
        response = None
        retry = True
        result = None
        count = 0
        log.debug(f'Loading data for {request_data} with {retries} retries')
        request_data = self.prepare_request(request_data)
        url = self.settings['url']
        while retry:
            try:
                count += 1
                if count > retries:
                    log.warning('Maximum number of retries reached. Giving up.')
                    log.debug(f'Reached max retries while loading {url}')
                else:
                    req = requests.get(url, params=request_data, timeout=self.settings['timeout'])
                    req.raise_for_status()
                    response = req.json()
                retry = False
            except requests.exceptions.Timeout as e:
                error = self.redact(str(e))
                utils.exchange_not_available_handler(error=error, shortify=False, sleep=2)
            except requests.exceptions.HTTPError as e:
                error = self.redact(str(e))
                if e.response.status_code == 429:
                    utils.ddos_protection_handler(error=error, sleep=1, shortify=False)
                else:
                    utils.generic_error_handler(self.redact(error))
            except requests.exceptions.RequestException as e:
                error = self.redact(str(e))
                log.warning(f"Fatal error connecting to {self.settings['url']}. Exception caught: {error}")
                retry = False

            if response:
                if response.get('error'):
                    utils.generic_error_handler(self.redact(response.get('error')))
                else:
                    result = response

        return result

    def retrieve_accounts(self):
        """ Gets the current balance for an account """
        self._accounts = {'ETH': {}}
        log.debug('Retrieving the account balances')
        balances = self.__load_retry({
            'action': 'balancemulti',
            'address': ','.join(self.settings['addresses'])
        })
        if balances.get('message') == 'OK':
            for balance in balances['result']:
                self._accounts['ETH'].update({
                    balance['account']: float(balance['balance'])/(1000000000000000000),
                })
        for account in self._accounts['ETH']:
            tokens = self.__load_retry({
                'action': 'tokenlist',
                'address': account,
            })
            if tokens.get('message') == 'OK':
                for token in tokens['result']:
                    token_name = token.get('symbol')
                    if not token_name or len(token_name) > 15:
                        break
                    if not self._accounts.get(token_name):
                        self._accounts.update({token_name: {}})

                    token_decimals = token.get('decimals', 0)
                    if not token_decimals:
                        token_decimals = 0

                    balance = token.get('balance', 0)
                    if not balance:
                        balance = 0

                    if int(token_decimals) > 0:
                        balance = int(balance) / (10**int(token_decimals))

                    self._accounts[token_name].update({
                        account: float(balance)
                    })

        log.log(5, f'Accounts: {self._accounts}')
        return self._accounts
