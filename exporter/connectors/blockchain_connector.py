#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Handles the blockchain.info data and communication """

import logging
import requests
from ..lib import utils
from .connector import Connector

log = logging.getLogger('crypto-exporter')


class BlockchainConnector(Connector):
    """ The BlockchainConnector class """
    settings = {}
    params = {
        'addresses': {
            'key_type': 'list',
            'default': None,
            'mandatory': True,
        },
        'url': {
            'key_type': 'string',
            'default': 'https://blockchain.info',
            'mandatory': False,
        },
    }

    def __init__(self):
        self.exchange = 'blockchain'
        self.params.update(super().params)  # merge with the global params
        self.settings = utils.gather_environ(self.params)
        super().__init__()

    def retrieve_accounts(self):
        """ Connects to the blockchain API and retrieves the account information """
        if not self.settings['addresses']:
            return
        addresses = '|'.join(self.settings['addresses'])
        url = f"{self.settings['url']}/balance"
        request_data = {
            'active': addresses,
        }

        try:
            r = requests.get(url, params=request_data, timeout=self.settings['timeout']).json()
        except (
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout
        ) as e:
            log.warning(f"Can't connect to {self.settings['url']}. Exception caught: {utils.short_msg(e)}")

        for address in self.settings['addresses']:
            if r.get(address):
                balance = float(int(r.get(address).get('final_balance')) / 100000000)
                if not self._accounts.get('BTC'):
                    self._accounts.update({'BTC': {}})
                self._accounts['BTC'].update({
                    address: balance,
                })
            else:
                log.warning('Could not retrieve balance. The result follows.')
                log.warning(f"{r.get('result')}: {r.get('message')}")
