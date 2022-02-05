#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Handles the exchange data and communication """

import logging
import ccxt
from ..lib import constants
from ..lib import utils
from .connector import Connector

log = logging.getLogger('crypto-exporter')


class CcxtConnector(Connector):
    """ The CCXT Connector class """

    settings = {}
    params = {
        'api_key': {
            'key_type': 'string',
            'default': None,
            'mandatory': False,
            'redact': True,
        },
        'api_secret': {
            'key_type': 'string',
            'default': None,
            'mandatory': False,
            'redact': True,
        },
        'api_uid': {
            'key_type': 'string',
            'default': None,
            'mandatory': False,
            'redact': True,
        },
        'api_pass': {
            'key_type': 'string',
            'default': None,
            'mandatory': False,
            'redact': True,
        },
        'enable_tickers': {
            'key_type': 'bool',
            'default': True,
            'mandatory': False,
        },
        'enable_transactions': {
            'key_type': 'bool',
            'default': False,
            'mandatory': False,
        },
        'disable_fetch_tickers': {
            'key_type': 'bool',
            'default': False,
            'mandatory': False,
        },
        'symbols': {
            'key_type': 'list',
            'default': None,
            'mandatory': False,
        },
        'reference_currencies': {
            'key_type': 'list',
            'default': None,
            'mandatory': False,
        },
        'default_exchange_type': {
            'key_type': 'string',
            'default': None,
            'mandatory': False,
        },
        'nonce': {
            'key_type': 'string',
            'default': 'milliseconds',
            'mandatory': False,
        },
    }

    def __init__(self, exchange):
        self.exchange = exchange
        self.params.update(super().params)  # merge with the global params
        self.settings = utils.gather_environ(self.params)
        self.settings['enable_authentication'] = None
        __exchange = getattr(ccxt, self.exchange)
        exchange_options = {
            'enableRateLimit': True,
            'nonce': getattr(__exchange, self.settings['nonce']),
            'defaultType': self.settings['default_exchange_type'],
            'timeout': self.settings['timeout'] * 1000,  # ccxt expects the timeout in milliseconds
        }
        self.__exchange = __exchange(exchange_options)
        self.__markets = None
        super().__init__()

    def get_enable_authentication(self):
        """ Returns the status of the authentication """
        return self.settings['enable_authentication']

    def _prepare_authentication(self):
        """ Checks if API_KEY and API_SECRET are set """
        if self.settings['enable_authentication'] is None:
            if self.settings.get('api_key') and self.settings.get('api_secret'):
                self.__exchange.apiKey = self.settings['api_key']
                self.__exchange.secret = self.settings['api_secret']
                if self.settings.get('api_pass'):
                    self.__exchange.password = self.settings['api_pass']
                if self.settings.get('api_uid'):
                    self.__exchange.uid = self.settings['api_uid']
                self.settings['enable_authentication'] = True
                log.debug('Authentication is configured')

    def __load_retry(self, method, *args, retries=3, **kwargs):
        """ Tries up to {retries} times to call the ccxt function and then gives up """
        data = None
        retry = True
        count = 0
        log.debug(f'Calling {method} with {retries} retries')
        while retry:
            try:
                count += 1
                if count > retries:
                    log.warning('Maximum number of retries reached. Giving up.')
                    log.debug(f'Reached max retries while calling {method} with args "{args}" and kwargs {kwargs}.')
                else:
                    func = getattr(self.__exchange, method)
                    data = func(*args, **kwargs)
                retry = False
            except KeyError as error:
                log.warning(f'Reloading markets. Exception occurred: {error}')
                self.__fetch_markets(force=True)
                retry = False
            except ccxt.DDoSProtection as error:
                utils.ddos_protection_handler(error=error)
            except ccxt.PermissionDenied as error:
                self.settings['enable_authentication'] = False
                utils.permission_denied_handler(error=error)
                retry = False
            except ccxt.AuthenticationError as error:
                self.settings['enable_authentication'] = False
                utils.authentication_error_handler(error=error)
                retry = False
            except (ccxt.ExchangeNotAvailable, ccxt.RequestTimeout, ccxt.ExchangeError) as error:
                utils.exchange_not_available_handler(error=error)
        return data

    def __process_tickers(self, tickers):
        """ Formats the tickers """
        # if tickers:
        try:
            for ticker in tickers:
                currencies = ticker.split('/')
                if len(currencies) == 2 and tickers[ticker].get('last'):
                    pair = {
                        'currency': currencies[0],
                        'reference_currency': currencies[1],
                        'value': float(tickers[ticker]['last']),
                    }

                    self._tickers.update({
                        f'{ticker}': pair
                    })
        except TypeError:
            log.debug('No tickers to process')
        log.log(5, f"Found these tickers: {self._tickers}")

    def __process_ledger_entry_native_amount(self, transaction):
        """ Processes the transaction and calculates the totals based on currency and native_amount """
        p = (None, None, None)
        if transaction.get('amount') and transaction.get('native_amount'):
            currency = transaction['amount']['currency']
            reference_currency = transaction['native_amount']['currency']
            if (
                    transaction.get('type') in ['buy', 'sell']
                    and not currency == reference_currency
            ):
                value = float(transaction['native_amount']['amount'])
                p = (currency, reference_currency, value)
        return p

    def __fetch_tickers(self):
        log.debug('Fetching tickers')
        tickers = self.__load_retry('fetch_tickers')
        return tickers

    def __fetch_each_ticker(self, symbols):
        log.log(5, f'Fetching for these individual entries: {symbols}')
        tickers = {}
        for symbol in symbols:
            retrieve_ticker = False
            if 'symbol' in symbol:  # this happens when the symbols are loaded by fetch_markets
                symbol = symbol['symbol']

            if (not self.settings['symbols'] and not self.settings['reference_currencies']):
                retrieve_ticker = True
            if self.settings['symbols'] and symbol in self.settings['symbols']:
                retrieve_ticker = True
            if self.settings['reference_currencies']:
                for currency in self.settings['reference_currencies']:
                    if currency == symbol.split('/')[1]:
                        retrieve_ticker = True

            if retrieve_ticker:
                tickers.update(self.__fetch_ticker(symbol))
        return tickers

    def __fetch_ticker(self, symbol):
        log.debug(f'Fetching ticker for symbol {symbol}')
        data = self.__load_retry('fetch_ticker', symbol)
        ticker = {}
        if data:
            ticker = {symbol: {'last': data['last']}}
        return ticker

    def __fetch_markets(self, force=False):
        """ Loads the markets and saves them in self.__markets """
        log.debug(f'Fetching markets with force={force}')
        if force or not self.__markets:
            self.__markets = self.__load_retry('fetch_markets', retries=5)
            log.log(5, f'Found these markets: {self.__markets}')
        markets = self.__markets
        return markets

    def __fetch_ledger(self, account, **kw):
        log.debug(f'Fetching ledger for {account} with kw={kw}')
        ledger = []
        params = {
            'account_id': account,
        }

        if kw.get('starting_after'):
            params.update({'starting_after': kw['starting_after']})
        if kw.get('start'):
            params.update({'start': kw['start']})
        if kw.get('end'):
            params.update({'end': kw['end']})

        fetched_ledger = self.__load_retry(method='fetch_ledger', params=params)
        if fetched_ledger:
            ledger = fetched_ledger

        if (
                hasattr(self.__exchange, 'last_json_response')
                and self.__exchange.last_json_response.get('pagination')
                and self.__exchange.last_json_response['pagination']['next_starting_after']
        ):
            ledger += self.__fetch_ledger(
                account=account,
                starting_after=self.__exchange.last_json_response['pagination']['next_starting_after'],
            )
        if (
                hasattr(self.__exchange, 'last_json_response')
                and self.__exchange.last_json_response.get('result')
                and self.__exchange.last_json_response['result'].get('count')
                and int(self.__exchange.last_json_response['result']['count']) > len(ledger)
        ):
            ledger += self.__fetch_ledger(account=account, end=ledger[0]['id'])
            ledger = [i for n, i in enumerate(ledger) if i not in ledger[n + 1:]]
        log.log(5, f'Found this ledger: {ledger} (entries: {len(ledger)})')
        return ledger

    def retrieve_tickers(self):
        """ Connects to the exchange, downloads the price tickers and saves them in self._tickers """
        if not self.settings.get('enable_tickers'):
            return

        if not self.__markets:
            self.__fetch_markets()

        log.debug('Retrieving tickers')
        tickers = {}
        if self.__exchange.has['fetchTickers'] and (not self.settings.get('disable_fetch_tickers')):
            tickers = self.__fetch_tickers()
        else:
            log.warning(constants.WARN_TICKER_SLOW_LOAD)
            tickers = self.__fetch_each_ticker(self.__fetch_markets())

        self.__process_tickers(tickers)

        log.log(5, f"Found the following ticker rates: {self._tickers}")

    def retrieve_accounts(self):
        """ Connects to the exchange, downloads the accounts data and saves it in self._accounts """
        self._prepare_authentication()
        if not self.settings['enable_authentication']:
            return

        if not self.__markets:
            self.__fetch_markets()

        log.debug('Retrieving accounts')
        accounts = self.__load_retry('fetch_balance')
        try:
            if accounts.get('total'):
                self._accounts = {}
                for currency in accounts['total']:
                    if not self._accounts.get(currency):
                        self._accounts.update({currency: {}})
                    self._accounts[currency].update({
                        'total': accounts['total'][currency],
                    })
        except AttributeError:
            log.debug('No accounts found to process')

        log.log(5, f"Found the following accounts: {self._accounts}")

    def __process_ledger_native_amount(self, ledger=None):
        if not ledger:
            ledger = []
        # for now only trades are supported
        transaction_type = 'trade'
        for entry in ledger:
            if entry['info'].get('native_amount'):
                currency, reference_currency, value = self.__process_ledger_entry_native_amount(entry['info'])
                if currency:
                    if not self._transactions.get((currency, reference_currency, transaction_type)):
                        self._transactions.update({
                            (currency, reference_currency, transaction_type): float(0),
                        })
                    self._transactions[(currency, reference_currency, transaction_type)] -= value

    def __process_ledger_refid(self, ledger=None):
        if not ledger:
            ledger = []
        for entry in ledger:
            # for now only trades are supported
            if entry['type'] == 'trade':
                # search for the pairs
                for pair in ledger:
                    if (
                            entry['referenceId']
                            and pair['referenceId']
                            and entry['referenceId'] == pair['referenceId']
                            and entry['currency'] != pair['currency']
                    ):
                        currency = pair['currency']
                        reference_currency = entry['currency']
                        transaction_type = entry['type']
                        value = float(entry['amount'])
                        if not self._transactions.get((currency, reference_currency, transaction_type)):
                            self._transactions.update({
                                (currency, reference_currency, transaction_type): float(0),
                            })
                        if entry['direction'] == 'in':
                            self._transactions[(currency, reference_currency, transaction_type)] += value
                        if entry['direction'] == 'out':
                            self._transactions[(currency, reference_currency, transaction_type)] -= value

    def retrieve_transactions(self):
        """
        Connects to the exchange and retrieves the transaction history

        Only supported for certain exchanges
        """
        if not self.settings.get('enable_transactions'):
            return
        self._prepare_authentication()
        if not self.settings['enable_authentication']:
            return

        if not self.__markets:
            self.__fetch_markets()
        if not self._accounts:
            self.retrieve_accounts()

        log.debug('Retrieving transactions')

        if self.__exchange.has['fetchLedger']:
            # Fetches the ledger for every account
            ledger = []
            for account in self._accounts:
                account_ledger = self.__fetch_ledger(account)
                if account_ledger and account_ledger[0]['info'].get('native_amount'):
                    ledger += account_ledger
                elif account_ledger and account_ledger[0]['info'].get('refid'):
                    ledger = account_ledger
                    break

            if (len(ledger) > 0 and ledger[0].get('info')):
                self._transactions = {}
                if ledger[0]['info'].get('native_amount'):
                    self.__process_ledger_native_amount(ledger)
                if ledger[0]['info'].get('refid'):
                    self.__process_ledger_refid(ledger)
