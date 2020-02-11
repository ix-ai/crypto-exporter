#!/usr/bin/env python3
""" Prometheus Exporter for Crypto Exchanges """

import time
from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily, StateSetMetricFamily
from .lib import constants


class CryptoCollector():
    """ The CryptoCollector creating Prometheus metrics """

    metrics = {
        'account_balance': None,
        'exchange_rate': None,
    }

    def __init__(self, exchange):
        """ Initializes the class """
        self.exchange = exchange
        # Exporter information
        self.metrics['crypto_exporter'] = self.get_metric_exporter_info()
        # Uptime
        self.metrics['uptime'] = self.get_metric_uptime()

    def get_metric_exporter_info(self):
        """ Information about the exporter """
        m = InfoMetricFamily(
            'crypto_exporter',
            f'Information about {__package__}',
            labels=['exchange', 'version', 'build']
        )
        return m.add_metric(
            value={'version': f'{constants.VERSION}', 'build': f'{constants.BUILD}'},
            labels=[f'{self.exchange.exchange}'],
        )

    def get_metric_uptime(self):
        """ Uptime information """
        m = GaugeMetricFamily(
            'uptime',
            f'Uptime of {__package__}',
            labels=['exchange']
        )
        return m.add_metric(
            value=time.time(),
            labels=[f'{self.exchange.exchange}'],
        )

    def get_metric_authentication(self):
        """ Shows if the current run was authenticated """
        m = StateSetMetricFamily(
            'authentication',
            'Shows if authentication is enabled',
            labels=['exchange'],
        )
        return m.add_metric(
            [f'{self.exchange.exchange}'],
            {'enabled': self.exchange.get_enable_authentication()},
        )

    def metric_account_balance(self):
        """ Returns an instance of GaugeMetricFamily initialized for account balance """
        return GaugeMetricFamily(
            'account_balance',
            'Account Balance',
            labels=['currency', 'account', 'exchange']
        )

    def metric_exchange_rate(self):
        """ Returns an instance of GaugeMetricFamily initialized for exchange rate """
        return GaugeMetricFamily(
            'exchange_rate',
            'Current exchange rates',
            labels=['currency', 'reference_currency', 'exchange']
        )

    def collect(self):
        """ This is the function that takes the exchange data and converts it to prometheus metrics """
        exchange = self.exchange
        metrics = self.metrics

        exchange.retrieve_tickers()
        tickers = exchange.get_tickers()
        metrics['exchange_rate'] = self.metric_exchange_rate()
        for rate in tickers:
            metrics['exchange_rate'].add_metric(
                value=tickers[rate]['value'],
                labels=[
                    f"{tickers[rate]['currency']}",
                    f"{tickers[rate]['reference_currency']}",
                    f'{exchange.exchange}',
                ]
            )

        exchange.retrieve_accounts()
        accounts = exchange.get_accounts()
        metrics['account_balance'] = self.metric_account_balance()
        for currency in accounts:
            for account_type in accounts[currency]:
                if accounts[currency].get(account_type,) and (accounts[currency].get(account_type, 0) > 0):
                    metrics['account_balance'].add_metric(
                        value=(accounts[currency][account_type]),
                        labels=[
                            f'{currency}',
                            f'{account_type}',
                            f'{exchange.exchange}',
                        ]
                    )

        metrics['authentication'] = self.get_metric_authentication()

        for metric in metrics.values():
            yield metric

    def describe(self):
        """ See https://github.com/prometheus/client_python#custom-collectors """
        return []
