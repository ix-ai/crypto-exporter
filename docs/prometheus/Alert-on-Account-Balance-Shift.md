# Alert on Account Balance Shift

Get a prometheus alert if there is any movement on any account:
```yml
groups:
  - name: crypto
    rules:
      - alert: balance_shift
        expr: delta(account_balance[3m]) != 0
        for: 30s
        labels:
          severity: 1
          fqdn: account-balance
        annotations:
          condition: delta(account_balance[3m]) != 0
          description: Balance shift for {{ .Labels.currency }} moved by {{ .Value }}
```
