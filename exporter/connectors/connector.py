#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" The Connector Class """


class Connector():
    """ The Class Definition """

    _tickers = {}
    _accounts = {}
    _transactions = {}
    params = {
        'timeout': {
            'key_type': 'int',
            'default': 10,  # in seconds
            'mandatory': False,
        },
    }
    settings = {}
    exchange = None

    def get_tickers(self):
        """ Returns the stored ticker rates """
        return self._tickers

    def get_accounts(self):
        """ Returns the accounts """
        return self._accounts

    def get_transactions(self):
        """ Returns the transaction history """
        return self._transactions

    def retrieve_tickers(self):
        """ Triggers the run to retrieve the tickers """

    def retrieve_accounts(self):
        """
        Triggers the run to populate self._accounts

        {
            SYMBOL: {
                ACCOUNT_NAME: float(value)
            },
        }

        """

    def retrieve_transactions(self):
        """ Triggers the run to retrieve the transactions """

    def redact(self, message: str) -> str:
        """
        Redacts all the sensitive information from the message
        """
        for param, values in self.params.items():
            if values.get('redact') and self.settings.get(param):
                message = message.replace(self.settings.get(param), '***REDACTED***')
        return message
