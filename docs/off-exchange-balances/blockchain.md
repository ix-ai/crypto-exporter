# BTC
Support for the BTC account balance is implemented by querying the [blockchain.info API](https://www.blockchain.com/api). The following environment variables are supported:

| **Variable**             | **Default**               | **Mandatory** | **Description**  |
|:-------------------------|:-------------------------:|:-------------:|:-----------------|
| `EXCHANGE`               | -                         | **YES**       | Set this to `blockchain` |
| `ADDRESSES`              | -                         | **YES**       | A comma separated list of BTC addresses |
| `URL`                    | `https://blockchain.info` | NO            | The base URL to query |

Additionally, the global variables `TIMEOUT`, `LOGLEVEL`, `GELF_HOST`, `GELF_PORT` and `PORT` are supported.
