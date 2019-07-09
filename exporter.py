#!/usr/bin/env python3
""" Prometheus Exporter for Crypto Exchanges """

import logging
import time
import os
import sys
import ccxt
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY, GaugeMetricFamily

LOG = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=os.environ.get("LOGLEVEL", "INFO"),
    format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class CryptoCollector():
    """ The CryptoCollector class """

    rates = {}
    accounts = {}
    has_api_credentials = False
    markets = None

    def __init__(self):
        if not os.environ.get('EXCHANGE'):
            raise ValueError("Missing EXCHANGE environment variable. See README.md.")

        self.exchange = os.environ.get('EXCHANGE')

        selected_exchange = getattr(ccxt, self.exchange)
        self.selected_exchange = selected_exchange({'nonce': ccxt.poloniex.milliseconds})
        if os.environ.get("API_KEY") and os.environ.get("API_SECRET"):
            self.selected_exchange.apiKey = os.environ.get("API_KEY")
            self.selected_exchange.secret = os.environ.get("API_SECRET")
            self.has_api_credentials = True

        if os.environ.get("API_UID"):
            self.selected_exchange.uid = os.environ.get("API_UID")

    def get_tickers(self):
        """ Connects to the exchange and downloads the price tickers """

        LOG.debug('Loading Markets')
        markets_loaded = False
        while markets_loaded is False:
            try:
                self.selected_exchange.loadMarkets(True)
                markets_loaded = True
            except (ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:
                LOG.warning('{}'.format(error))
                time.sleep(1)

        if self.selected_exchange.has['fetchTickers']:
            LOG.debug('Loading Tickers')
            tickers = self.selected_exchange.fetch_tickers()
        elif self.selected_exchange.has['fetchCurrencies']:
            tickers = {}
            for symbol in self.selected_exchange.symbols:
                LOG.debug('Loading Symbol {}'.format(symbol))
                try:
                    tickers.update({
                        symbol: {
                            'last': self.selected_exchange.fetch_ticker(symbol)['last']
                        }
                    })
                except (ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:
                    LOG.warning('{}'.format(error))
                time.sleep(1)  # don't hit the rate limit
        else:
            tickers = {}
            if not self.markets:
                LOG.debug('Fetching markets')
                self.markets = self.selected_exchange.fetch_markets()
            for market in self.markets:
                symbol = market.get('symbol')
                LOG.debug('Loading Symbol {}'.format(symbol))
                try:
                    tickers.update({
                        symbol: {
                            'last': self.selected_exchange.fetch_ticker(symbol)['last']
                        }
                    })
                except (ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:
                    LOG.warning('{}'.format(error))
                time.sleep(1)  # don't hit the rate limit

        for ticker in tickers:
            currencies = ticker.split('/')
            if len(currencies) == 2 and tickers[ticker].get('last'):
                pair = {
                    'source_currency': currencies[0],
                    'target_currency': currencies[1],
                    'value': float(tickers[ticker]['last']),
                }

                self.rates.update({
                    '{}'.format(ticker): pair
                })

        LOG.debug('Found the following ticker rates: {}'.format(self.rates))

    def get_accounts(self):
        """ Gets the account data from the exchange """

        if self.has_api_credentials:
            accounts = {}
            try:
                accounts = self.selected_exchange.fetch_balance()
                self.accounts = {}
            except (ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:
                LOG.warning("{}".format(error))
            except ccxt.AuthenticationError:
                LOG.error("Can't authenticate to read the accounts. Check your API_KEY/API_SECRET/API_UID.")
                LOG.error("Disabling the credentials.")
                self.has_api_credentials = False

            if accounts.get('free'):
                for currency in accounts['free']:
                    if not self.accounts.get(currency):
                        self.accounts.update({currency: {}})
                    self.accounts[currency].update({'free': accounts['free'][currency]})

            if accounts.get('used'):
                for currency in accounts['used']:
                    if not self.accounts.get(currency):
                        self.accounts.update({currency: {}})
                    self.accounts[currency].update({'used': accounts['used'][currency]})

        LOG.debug('Found the following accounts: {}'.format(self.accounts))

    def collect(self):
        """ The only function that does the collecting around here """
        metrics = {
            'exchange_rate': GaugeMetricFamily(
                'exchange_rate',
                'Current exchange rates',
                labels=['source_currency', 'target_currency', 'exchange']
            ),
            'account_balance': GaugeMetricFamily(
                'account_balance',
                'Account Balance',
                labels=['source_currency', 'currency', 'account', 'type']
            ),
        }
        self.get_tickers()
        for rate in self.rates:
            metrics['exchange_rate'].add_metric(
                value=self.rates[rate]['value'],
                labels=[
                    self.rates[rate]['source_currency'],
                    self.rates[rate]['target_currency'],
                    self.exchange
                ]
            )

        self.get_accounts()
        for currency in self.accounts:
            for account_type in self.accounts[currency]:  # free / used
                if self.accounts[currency][account_type] > 0:
                    metrics['account_balance'].add_metric(
                        value=(self.accounts[currency][account_type]),
                        labels=[
                            currency,
                            currency,
                            account_type,
                            self.exchange
                        ]
                    )

        for metric in metrics.values():
            yield metric

    def describe(self):
        """ See https://github.com/prometheus/client_python#custom-collectors """
        return []


if __name__ == '__main__':
    LOG.info("Starting")
    REGISTRY.register(CryptoCollector())
    start_http_server(9308)
    while True:
        time.sleep(1)
