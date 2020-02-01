#!/usr/bin/env python3
""" Prometheus Exporter for Crypto Exchanges """

from prometheus_client.core import GaugeMetricFamily


class CryptoCollector():
    """ The CryptoCollector creating Prometheus metrics """

    def __init__(self, exchange):
        """ Initializes the class """
        self.exchange = exchange

    def collect(self):
        """ This is the function that takes the exchange data and converts it to prometheus metrics """
        exchange = self.exchange
        metrics = {
            'exchange_rate': GaugeMetricFamily(
                'exchange_rate',
                'Current exchange rates',
                labels=['currency', 'reference_currency', 'exchange', 'source_currency', 'target_currency']
            ),
            'account_balance': GaugeMetricFamily(
                'account_balance',
                'Account Balance',
                labels=['currency', 'account', 'exchange', 'source_currency']
            ),
        }
        exchange.retrieve_tickers()
        tickers = exchange.get_tickers()
        for rate in tickers:
            metrics['exchange_rate'].add_metric(
                value=tickers[rate]['value'],
                labels=[
                    tickers[rate]['currency'],
                    tickers[rate]['reference_currency'],
                    exchange.exchange,
                    tickers[rate]['currency'],
                    tickers[rate]['reference_currency'],
                ]
            )

        exchange.retrieve_accounts()
        accounts = exchange.get_accounts()
        for currency in accounts:
            for account_type in accounts[currency]:
                if accounts[currency].get(account_type,) and (accounts[currency].get(account_type, 0) > 0):
                    metrics['account_balance'].add_metric(
                        value=(accounts[currency][account_type]),
                        labels=[
                            currency,
                            account_type,
                            exchange.exchange,
                            currency,
                        ]
                    )

        for metric in metrics.values():
            yield metric

    def describe(self):
        """ See https://github.com/prometheus/client_python#custom-collectors """
        return []
