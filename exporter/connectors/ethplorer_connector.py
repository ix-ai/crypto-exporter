#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Handles the ethplorer data and communication """

import logging
import requests
from ..lib import utils
from .connector import Connector

log = logging.getLogger('crypto-exporter')


class EthplorerConnector(Connector):
    """ The EthplorerConnector class """

    settings = {}
    params = {
        'api_key': {
            'key_type': 'string',
            'default': 'freekey',
            'mandatory': False,
            'redact': True,
        },
        'addresses': {
            'key_type': 'list',
            'default': None,
            'mandatory': True,
        },
        'url': {
            'key_type': 'string',
            'default': 'https://api.ethplorer.io',
            'mandatory': False,
        },
    }

    def __init__(self):
        self.exchange = 'ethplorer'
        self.params.update(super().params)  # merge with the global params
        self.settings = utils.gather_environ(self.params)
        self.settings.update({'enable_authentication': True})
        super().__init__()

    def prepare_request(self, request_data: dict) -> dict:
        """ Checks the request_data and adds the missing keys """
        if not request_data.get('apiKey'):
            request_data.update({'apiKey': self.settings['api_key']})
        return request_data

    def __load_retry(self, account, retries=5):
        """ Tries up to {retries} times to call the api and then gives up """
        response = None
        retry = True
        result = None
        count = 0
        log.debug(f'Loading account data for {account} with {retries} retries')
        request_data = self.prepare_request({})
        url = f"{self.settings['url']}/getAddressInfo/{account}"
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
                if e.response.status_code == 403:
                    utils.authentication_error_handler(error)
                    self.settings['enable_authentication'] = False
                    retry = False
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
        for address in self.settings['addresses']:
            if not self.settings['enable_authentication']:
                return {}
            data = self.__load_retry(address, retries=2)
            if data:
                if data.get('ETH'):
                    self._accounts['ETH'].update({
                        address: float(data['ETH']['balance'])
                    })
                if data.get('tokens'):
                    for token in data['tokens']:
                        token_name = token['tokenInfo'].get('symbol')
                        # Ignores the low quality tokens
                        if (
                                len(token_name) > 15
                                or not token_name
                        ):
                            break

                        token_decimals = int(token['tokenInfo'].get('decimals', 0))
                        if token_decimals > 0:
                            balance = int(token['balance']) / (10**token_decimals)
                        else:
                            balance = int(token['balance'])

                        if token_name not in self._accounts:
                            self._accounts.update({token_name: {}})

                        self._accounts[token_name].update({
                            address: float(balance)
                        })

        log.log(5, f'Accounts: {self._accounts}')
        return self._accounts
