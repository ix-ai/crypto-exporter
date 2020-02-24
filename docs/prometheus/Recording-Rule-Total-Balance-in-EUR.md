# Recording Rule: Total Balance in EUR

Based on the exchange rate of Kraken, how much EUR is it in all accounts (discarding everything <1 EUR)?
```yml
groups:
  - name: crypto
    rules:
      - record: 'balance_total:kraken:eur'
        expr: |
            (sum by (currency) (max by (currency, account)(avg_over_time(account_balance[10m]) > 0))
            * on (currency)
            max by (currency)(exchange_rate{exchange="kraken", reference_currency="EUR"}) > 0) > 1
```

Use then the metric `balance_total:kraken:eur`
