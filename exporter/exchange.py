#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Handles the exchange data and communication """

import ccxt
from .lib import constants
from .lib import handlers
from .lib.log import ExporterLogging as log


class Exchange():
    """ The Exchange class """

    settings = {}
    __settings = {}

    def __init__(self, options):
        # Mandatory attributes
        self.exchange = options['exchange']
        self.settings['nonce'] = options.get('nonce', 'milliseconds')
        __exchange = getattr(ccxt, self.exchange)
        self.__exchange = __exchange({
            'nonce': getattr(__exchange, self.settings['nonce']),
            'enableRateLimit': True,
        })

        # Settable defaults
        self.settings['enable_tickers'] = options.get('enable_tickers', True)
        self.settings['symbols'] = options.get('symbols')
        self.settings['reference_currencies'] = options.get('reference_currencies')

        # Convert the strings to lists
        if self.settings['symbols']:
            self.settings['symbols'] = self.settings['symbols'].split(',')
        if self.settings['reference_currencies']:
            self.settings['reference_currencies'] = self.settings['reference_currencies'].split(',')

        # Authentication data
        self.__settings['api_key'] = options.get('api_key')
        self.__settings['api_secret'] = options.get('api_secret')
        self.__settings['api_pass'] = options.get('api_pass')
        self.__settings['api_uid'] = options.get('api_uid')

        # Exporter Data
        self.__settings['accounts'] = {}
        self.__settings['currencies'] = {}
        self.__settings['tickers'] = {}

        # Internal settings and lists
        log.LOG.info('Loading Markets')
        markets_loaded = False
        while markets_loaded is False:
            try:
                self.__exchange.loadMarkets(True)
                markets_loaded = True
                log.LOG.info('Markets loaded')
            except ccxt.DDoSProtection as error:
                handlers.DDoSProtectionHandler(error=error)
            except (ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:  # pylint: disable=duplicate-except
                handlers.ExchangeNotAvailableHandler(error=error)
        self.__markets = self.__exchange.markets
        self.__settings['enable_authentication'] = None

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
                log.LOG.debug('Authentication is configured')

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
        log.LOG.info('Loading Tickers')
        tickers = {}
        tickers_loaded = False
        while tickers_loaded is False:
            try:
                tickers = self.__exchange.fetch_tickers()
                tickers_loaded = True
            except ccxt.DDoSProtection as error:
                handlers.DDoSProtectionHandler(error=error)
            except (ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:  # pylint: disable=duplicate-except
                handlers.ExchangeNotAvailableHandler(error=error)
            except ccxt.PermissionDenied as error:  # pylint: disable=duplicate-except
                handlers.PermissionDeniedHandler(error=error)
        return tickers

    def __fetch_each_ticker(self, symbols):
        log.LOG.info('Loading each ticker rate individually')
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
                    if '/{}'.format(currency) in symbol:
                        retrieve_ticker = True

            if retrieve_ticker:
                tickers.update(self.__fetch_ticker(symbol))
        return tickers

    def __fetch_ticker(self, symbol):
        log.LOG.info('Loading ticker for symbol {}'.format(symbol))
        ticker = None
        tickers_loaded = False
        while tickers_loaded is False:
            try:
                ticker = {symbol: {'last': self.__exchange.fetch_ticker(symbol)['last']}}
                tickers_loaded = True
            except ccxt.DDoSProtection as error:
                handlers.DDoSProtectionHandler(error=error)
            except (ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:  # pylint: disable=duplicate-except
                handlers.ExchangeNotAvailableHandler(error=error)
        if ticker:
            return ticker

    def retrieve_tickers(self):
        """ Connects to the exchange, downloads the price tickers and saves them in self.__settings['tickers'] """
        if not self.settings.get('enable_tickers'):
            return
        log.LOG.info('Loading tickers')
        tickers = {}
        if self.__exchange.has['fetchTickers']:
            tickers = self.__fetch_tickers()
        elif self.__exchange.has['fetchCurrencies']:
            log.LOG.warning(constants.WARN_TICKER_SLOW_LOAD)
            log.LOG.debug('Found these symbols: {}'.format(self.__exchange.symbols))
            tickers = self.__fetch_each_ticker(self.__exchange.symbols)
        else:
            if not self.__markets:
                log.LOG.warning(constants.WARN_TICKER_SLOW_LOAD)
                markets_fetched = False
                log.LOG.info('Fetching markets')
                while markets_fetched is False:
                    try:
                        self.__markets = self.__exchange.fetch_markets()
                        markets_fetched = True
                    except ccxt.DDoSProtection as error:
                        handlers.DDoSProtectionHandler(error=error, sleep=15)
                    except (ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:  # pylint: disable=duplicate-except
                        handlers.ExchangeNotAvailableHandler(error=error)
                    except ccxt.PermissionDenied as error:  # pylint: disable=duplicate-except
                        handlers.PermissionDeniedHandler(error=error)

            log.LOG.debug('Found these markets: {}'.format(self.__exchange.markets))
            tickers = self.__fetch_each_ticker(self.__markets)

        self.__process_tickers(tickers)

        log.LOG.debug('Found the following ticker rates: {}'.format(self.__settings['tickers']))

    def retrieve_accounts(self):
        """ Connects to the exchange, downloads the accounts data and saves it in self.__settings['accounts'] """
        self._prepare_authentication()
        if not self.__settings['enable_authentication']:
            return

        log.LOG.info('Loading accounts')
        accounts = {}
        try:
            accounts = self.__exchange.fetch_balance()
            self.__settings['accounts'] = {}
        except (ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:
            handlers.ExchangeNotAvailableHandler(error=error)
        except (ccxt.AuthenticationError, ccxt.ExchangeError) as error:  # pylint: disable=duplicate-except
            handlers.AuthenticationErrorHandler(error=error, nonce=self.settings['nonce'])
            self.__settings['enable_authentication'] = False
        except ccxt.DDoSProtection as error:  # pylint: disable=duplicate-except
            handlers.DDoSProtectionHandler(error=error)
        except ccxt.PermissionDenied as error:  # pylint: disable=duplicate-except
            handlers.PermissionDeniedHandler(error=error)

        if accounts.get('total'):
            for currency in accounts['total']:
                if not self.__settings['accounts'].get(currency):
                    self.__settings['accounts'].update({currency: {}})
                self.__settings['accounts'][currency].update({
                    'total': accounts['total'][currency],
                })

        log.LOG.debug('Found the following accounts: {}'.format(self.__settings['accounts']))
