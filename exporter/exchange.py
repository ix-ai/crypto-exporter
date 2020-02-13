#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Handles the exchange data and communication """

import logging
import inspect
import time
import ccxt
from .lib import constants

log = logging.getLogger(__package__)


def short_msg(msg, chars=75):
    """ Truncates the message to {chars} characters and adds three dots at the end """
    return (str(msg)[:chars] + '..') if len(str(msg)) > chars else str(msg)


def DDoSProtectionHandler(error, sleep=1):
    """ Prints a warning and sleeps """
    caller = inspect.stack()[1].function
    log.warning(f'({caller}) Rate limit has been reached. Sleeping for {sleep}s. The exception: {short_msg(error)}')
    time.sleep(sleep)  # don't hit the rate limit


def ExchangeNotAvailableHandler(error, sleep=10):
    """ Prints an error and sleeps """
    caller = inspect.stack()[1].function
    log.error(f'({caller}) The exchange API could not be reached. Sleeping for {sleep}s. The error: {short_msg(error)}')
    time.sleep(sleep)  # don't hit the rate limit


def AuthenticationErrorHandler(error, nonce=''):
    """ Logs hints about the authentication error """
    caller = inspect.stack()[1].function
    error = short_msg(error)
    message = f"({caller}) Can't authenticate to read the accounts."
    if 'request timestamp expired' in str(error):
        if nonce == 'milliseconds':
            message += ' Set NONCE to `seconds` and try again.'
        elif nonce == 'seconds':
            message += ' Set NONCE to `milliseconds` and try again.'
    else:
        message += f' Check your API_KEY/API_SECRET/API_UID/API_PASS. Disabling the credentials. The exception: {error}'
    log.error(message)


def PermissionDeniedHandler(error):
    """ Prints error and gives hints about the cause """
    caller = inspect.stack()[1].function
    error = short_msg(error)
    log.error(f'({caller}) The exchange reports "permission denied": {error} Check the API token permissions')


class Exchange():
    """ The Exchange class """

    settings = {}
    __settings = {}

    def __init__(self, **kwargs):
        # Mandatory attributes
        log.info('Initializing exchange...')

        self.exchange = kwargs['exchange']
        self.settings['nonce'] = kwargs.get('nonce', 'milliseconds')
        __exchange = getattr(ccxt, self.exchange)

        exchange_options = {
            'nonce': getattr(__exchange, self.settings['nonce']),
            'enableRateLimit': True,
        }
        if kwargs.get('default_exchange_type'):
            exchange_options.update({'defaultType': kwargs['default_exchange_type']})
        self.__exchange = __exchange(exchange_options)

        # Settable defaults
        self.settings['enable_tickers'] = kwargs.get('enable_tickers', True)
        self.settings['enable_transactions'] = kwargs.get('enable_transactions', True)
        self.settings['symbols'] = kwargs.get('symbols')
        self.settings['reference_currencies'] = kwargs.get('reference_currencies')

        # Convert the strings to lists
        if self.settings['symbols']:
            self.settings['symbols'] = self.settings['symbols'].split(',')
        self.__settings['reference_currencies'] = []
        if self.settings['reference_currencies']:
            self.__settings['reference_currencies'] = self.settings['reference_currencies'].split(',')

        # Authentication data
        self.__settings['api_key'] = kwargs.get('api_key')
        self.__settings['api_secret'] = kwargs.get('api_secret')
        self.__settings['api_pass'] = kwargs.get('api_pass')
        self.__settings['api_uid'] = kwargs.get('api_uid')

        # Exporter Data
        self.__settings['accounts'] = {}
        self.__settings['tickers'] = {}
        self.__settings['transactions'] = {}

        # Internal settings and lists
        self.__settings['enable_authentication'] = None
        self.__markets = None
        log.info('Exchange initialized')

    def get_tickers(self):
        """ Returns the stored ticker rates """
        return self.__settings['tickers']

    def get_accounts(self):
        """ Returns the accounts """
        return self.__settings['accounts']

    def get_enable_authentication(self):
        """ Returns the status of the authentication """
        return self.__settings['enable_authentication']

    def get_transactions(self):
        """ Returns the transaction history """
        return self.__settings['transactions']

    def _prepare_authentication(self):
        """ Checks if API_KEY and API_SECRET are set """
        if self.__settings['enable_authentication'] is None:
            if self.__settings.get('api_key') and self.__settings.get('api_secret'):
                self.__exchange.apiKey = self.__settings['api_key']
                self.__exchange.secret = self.__settings['api_secret']
                if self.__settings.get('api_pass'):
                    self.__exchange.password = self.__settings['api_pass']
                if self.__settings.get('api_uid'):
                    self.__exchange.uid = self.__settings['api_uid']
                self.__settings['enable_authentication'] = True
                log.debug('Authentication is configured')

    def __load_retry(self, method, *args, retries=5, **kwargs):
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
                DDoSProtectionHandler(error=error)
            except ccxt.AuthenticationError as error:  # pylint: disable=duplicate-except
                self.__settings['enable_authentication'] = False
                AuthenticationErrorHandler(error=error)
                retry = False
            except ccxt.PermissionDenied as error:  # pylint: disable=duplicate-except
                self.__settings['enable_authentication'] = False
                PermissionDeniedHandler(error=error)
                retry = False
            except (ccxt.ExchangeNotAvailable, ccxt.RequestTimeout, ccxt.ExchangeError) as error:  # pylint: disable=duplicate-except
                ExchangeNotAvailableHandler(error=error)
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

                    self.__settings['tickers'].update({
                        f'{ticker}': pair
                    })
        except TypeError:
            log.debug('No tickers to process')
        log.debug(f"Found these tickers: {self.__settings['tickers']}")

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
        log.debug(f'Fetching for these individual entries: {symbols}')
        tickers = {}
        for symbol in symbols:
            retrieve_ticker = False
            if 'symbol' in symbol:  # this happens when the symbols are loaded by fetch_markets
                symbol = symbol['symbol']

            if (not self.settings['symbols'] and not self.__settings['reference_currencies']):
                retrieve_ticker = True
            if self.settings['symbols'] and symbol in self.settings['symbols']:
                retrieve_ticker = True
            if self.__settings['reference_currencies']:
                for currency in self.__settings['reference_currencies']:
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
            log.debug(f'Found these markets: {self.__markets}')
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

        ledger += self.__load_retry(method='fetch_ledger', params=params)

        if (
                self.__exchange.last_json_response.get('pagination')
                and self.__exchange.last_json_response['pagination']['next_starting_after']
        ):
            ledger += self.__fetch_ledger(
                account=account,
                starting_after=self.__exchange.last_json_response['pagination']['next_starting_after'],
            )
        if (
                self.__exchange.last_json_response.get('result')
                and self.__exchange.last_json_response['result'].get('count')
                and int(self.__exchange.last_json_response['result']['count']) > len(ledger)
        ):
            ledger += self.__fetch_ledger(account=account, end=ledger[0]['id'])
            ledger = [i for n, i in enumerate(ledger) if i not in ledger[n + 1:]]
        log.debug(f'Found this ledger: {ledger} (entries: {len(ledger)})')
        return ledger

    def retrieve_tickers(self):
        """ Connects to the exchange, downloads the price tickers and saves them in self.__settings['tickers'] """
        if not self.settings.get('enable_tickers'):
            return

        if not self.__markets:
            self.__fetch_markets()

        log.info('Retrieving tickers')
        tickers = {}
        if self.__exchange.has['fetchTickers']:
            tickers = self.__fetch_tickers()
        else:
            log.warning(constants.WARN_TICKER_SLOW_LOAD)
            tickers = self.__fetch_each_ticker(self.__fetch_markets())

        self.__process_tickers(tickers)

        log.debug(f"Found the following ticker rates: {self.__settings['tickers']}")

    def retrieve_accounts(self):
        """ Connects to the exchange, downloads the accounts data and saves it in self.__settings['accounts'] """
        self._prepare_authentication()
        if not self.__settings['enable_authentication']:
            return

        if not self.__markets:
            self.__fetch_markets()

        log.info('Retrieving accounts')
        accounts = self.__load_retry('fetch_balance')
        try:
            if accounts.get('total'):
                self.__settings['accounts'] = {}
                for currency in accounts['total']:
                    if not self.__settings['accounts'].get(currency):
                        self.__settings['accounts'].update({currency: {}})
                    self.__settings['accounts'][currency].update({
                        'total': accounts['total'][currency],
                    })
        except AttributeError:
            log.debug('No accounts found to process')

        log.debug(f"Found the following accounts: {self.__settings['accounts']}")

    def __process_ledger_native_amount(self, ledger=None):
        if not ledger:
            ledger = []
        # for now only trades are supported
        transaction_type = 'trade'
        for entry in ledger:
            if entry['info'].get('native_amount'):
                currency, reference_currency, value = self.__process_ledger_entry_native_amount(entry['info'])
                if currency:
                    if not self.__settings['transactions'].get((currency, reference_currency, transaction_type)):
                        self.__settings['transactions'].update({
                            (currency, reference_currency, transaction_type): float(0),
                        })
                    self.__settings['transactions'][(currency, reference_currency, transaction_type)] -= value

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
                        if not self.__settings['transactions'].get((currency, reference_currency, transaction_type)):
                            self.__settings['transactions'].update({
                                (currency, reference_currency, transaction_type): float(0),
                            })
                        if entry['direction'] == 'in':
                            self.__settings['transactions'][(currency, reference_currency, transaction_type)] += value
                        if entry['direction'] == 'out':
                            self.__settings['transactions'][(currency, reference_currency, transaction_type)] -= value

    def retrieve_transactions(self):
        """
        Connects to the exchange and retrieves the transaction history

        Only supported for certain exchanges
        """
        if not self.settings.get('enable_transactions'):
            return
        self._prepare_authentication()
        if not self.__settings['enable_authentication']:
            return

        if not self.__markets:
            self.__fetch_markets()
        if not self.__settings['accounts']:
            self.retrieve_accounts()

        log.info('Retrieving transactions')

        if self.__exchange.has['fetchLedger']:
            # Fetches the ledger for every account
            ledger = []
            for account in self.__settings['accounts']:
                account_ledger = self.__fetch_ledger(account)
                if account_ledger and account_ledger[0]['info'].get('native_amount'):
                    ledger += account_ledger
                elif account_ledger and account_ledger[0]['info'].get('refid'):
                    ledger = account_ledger
                    break

            if (len(ledger) > 0 and ledger[0].get('info')):
                self.__settings['transactions'] = {}
                if ledger[0]['info'].get('native_amount'):
                    self.__process_ledger_native_amount(ledger)
                if ledger[0]['info'].get('refid'):
                    self.__process_ledger_refid(ledger)
