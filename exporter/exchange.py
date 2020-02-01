#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Handles the exchange data and communication """

import logging
import inspect
import time
import ccxt
from .lib import constants

log = logging.getLogger('crypto-exporter')


def DDoSProtectionHandler(error, sleep=15):
    """ Prints a warning and sleeps """
    log.warning(
        '({}) Rate limit has been reached.'.format(inspect.stack()[1].function),
        'Sleeping for {}s. The exception: {}'.format(sleep, error),
    )
    time.sleep(sleep)  # don't hit the rate limit


def ExchangeNotAvailableHandler(error, sleep=10):
    """ Prints an error and sleeps """
    log.error(
        '({}) The exchange API could not be reached.'.format(inspect.stack()[1].function),
        'Sleeping for {}. The error: {}'.format(sleep, error),
    )
    time.sleep(sleep)  # don't hit the rate limit


def AuthenticationErrorHandler(error, nonce=''):
    """ Logs hints about the authentication error """
    message = "({}) Can't authenticate to read the accounts.".format(inspect.stack()[1].function)
    if 'request timestamp expired' in str(error):
        if nonce == 'milliseconds':
            message += ' Set NONCE to `seconds` and try again.'
        elif nonce == 'seconds':
            message += ' Set NONCE to `milliseconds` and try again.'
    else:
        message += '{} The exception: {}'.format(
            " Check your API_KEY/API_SECRET/API_UID. Disabling the credentials.",
            str(error)
        )
    log.error(message)


def PermissionDeniedHandler(error):
    """ Prints error and gives hints about the cause """
    log.error(
        '({}) The exchange reports "permission denied": {}'.format(inspect.stack()[1].function, error),
        'Check the API token permissions',
    )


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
        self.__exchange = __exchange({
            'nonce': getattr(__exchange, self.settings['nonce']),
            'enableRateLimit': True,
        })

        # Settable defaults
        self.settings['enable_tickers'] = kwargs.get('enable_tickers', True)
        self.settings['symbols'] = kwargs.get('symbols')
        self.settings['reference_currencies'] = kwargs.get('reference_currencies')

        # Convert the strings to lists
        if self.settings['symbols']:
            self.settings['symbols'] = self.settings['symbols'].split(',')
        if self.settings['reference_currencies']:
            self.settings['reference_currencies'] = self.settings['reference_currencies'].split(',')

        # Authentication data
        self.__settings['api_key'] = kwargs.get('api_key')
        self.__settings['api_secret'] = kwargs.get('api_secret')
        self.__settings['api_pass'] = kwargs.get('api_pass')
        self.__settings['api_uid'] = kwargs.get('api_uid')

        # Exporter Data
        self.__settings['accounts'] = {}
        self.__settings['currencies'] = {}
        self.__settings['tickers'] = {}

        # Internal settings and lists
        self.__settings['enable_authentication'] = None
        self.__markets = None
        self.__fetch_markets()
        log.info('Exchange initialized')

    def get_tickers(self):
        """ Returns the stored ticker rates """
        return self.__settings['tickers']

    def get_accounts(self):
        """ Returns the accounts """
        return self.__settings['accounts']

    def _prepare_authentication(self):
        """ Checks if API_KEY and API_SECRET are set """
        if self.settings.get('enable_authentication') is None:
            if self.__settings.get('api_key') and self.__settings.get('api_secret'):
                self.__exchange.apiKey = self.__settings['api_key']
                self.__exchange.secret = self.__settings['api_secret']
                if self.__settings.get('api_pass'):
                    self.__exchange.password = self.__settings['api_pass']
                if self.__settings.get('api_uid'):
                    self.__exchange.uid = self.__settings['api_uid']
                self.__settings['enable_authentication'] = True
                log.debug('Authentication is configured')

    def __process_tickers(self, tickers):
        """ Formats the tickers """
        for ticker in tickers:
            currencies = ticker.split('/')
            if len(currencies) == 2 and tickers[ticker].get('last'):
                pair = {
                    'currency': currencies[0],
                    'reference_currency': currencies[1],
                    'value': float(tickers[ticker]['last']),
                }

                self.__settings['tickers'].update({
                    '{}'.format(ticker): pair
                })

    def __fetch_tickers(self):
        log.info('Loading tickers')
        tickers = {}
        tickers_loaded = False
        while tickers_loaded is False:
            try:
                tickers = self.__exchange.fetch_tickers()
                tickers_loaded = True
            except ccxt.DDoSProtection as error:
                DDoSProtectionHandler(error=error)
            except (ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:  # pylint: disable=duplicate-except
                ExchangeNotAvailableHandler(error=error)
            except ccxt.PermissionDenied as error:  # pylint: disable=duplicate-except
                PermissionDeniedHandler(error=error)
        return tickers

    def __fetch_each_ticker(self, symbols):
        log.info('Loading each ticker rate individually')
        log.debug('Loading for these individual entries: {}'.format(symbols))
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
        log.info('Loading ticker for symbol {}'.format(symbol))
        ticker = None
        tickers_loaded = False
        while tickers_loaded is False:
            try:
                ticker = {symbol: {'last': self.__exchange.fetch_ticker(symbol)['last']}}
                tickers_loaded = True
            except ccxt.DDoSProtection as error:
                DDoSProtectionHandler(error=error)
            except (ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:  # pylint: disable=duplicate-except
                ExchangeNotAvailableHandler(error=error)
        if ticker:
            return ticker

    def __fetch_markets(self):
        log.info('Fetching markets')
        markets_fetched = False
        if not self.__markets:
            while markets_fetched is False:
                try:
                    self.__markets = self.__exchange.fetch_markets()
                    markets_fetched = True
                except ccxt.DDoSProtection as error:
                    DDoSProtectionHandler(error=error, sleep=15)
                except (ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:  # pylint: disable=duplicate-except
                    ExchangeNotAvailableHandler(error=error)
                except ccxt.PermissionDenied as error:  # pylint: disable=duplicate-except
                    PermissionDeniedHandler(error=error)
                log.debug('Found these markets: {}'.format(self.__markets))
        markets = self.__markets
        return markets

    def retrieve_tickers(self):
        """ Connects to the exchange, downloads the price tickers and saves them in self.__settings['tickers'] """
        if not self.settings.get('enable_tickers'):
            return
        log.info('Retrieving tickers')
        tickers = {}
        if self.__exchange.has['fetchTickers']:
            tickers = self.__fetch_tickers()
        else:
            log.warning(constants.WARN_TICKER_SLOW_LOAD)
            tickers = self.__fetch_each_ticker(self.__markets)

        self.__process_tickers(tickers)

        log.debug('Found the following ticker rates: {}'.format(self.__settings['tickers']))

    def retrieve_accounts(self):
        """ Connects to the exchange, downloads the accounts data and saves it in self.__settings['accounts'] """
        self._prepare_authentication()
        if not self.__settings['enable_authentication']:
            return

        log.info('Retrieving accounts')
        accounts = {}
        try:
            accounts = self.__exchange.fetch_balance()
            self.__settings['accounts'] = {}
        except (ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:
            ExchangeNotAvailableHandler(error=error)
        except (ccxt.AuthenticationError, ccxt.ExchangeError) as error:  # pylint: disable=duplicate-except
            AuthenticationErrorHandler(error=error, nonce=self.settings['nonce'])
            self.__settings['enable_authentication'] = False
        except ccxt.DDoSProtection as error:  # pylint: disable=duplicate-except
            DDoSProtectionHandler(error=error)
        except ccxt.PermissionDenied as error:  # pylint: disable=duplicate-except
            PermissionDeniedHandler(error=error)

        if accounts.get('total'):
            for currency in accounts['total']:
                if not self.__settings['accounts'].get(currency):
                    self.__settings['accounts'].update({currency: {}})
                self.__settings['accounts'][currency].update({
                    'total': accounts['total'][currency],
                })

        log.debug('Found the following accounts: {}'.format(self.__settings['accounts']))
