# Stellar
Support for the Stellar account balance is implemented by querying the [stellar horizon server](https://horizon.stellar.org/). The following environment variables are supported:

| **Variable**             | **Default**                    | **Mandatory** | **Description**  |
|:-------------------------|:------------------------------:|:-------------:|:-----------------|
| `EXCHANGE`               | -                              | **YES**       | Set this to `stellar` |
| `ADDRESSES`              | -                              | **YES**       | A comma separated list of Ripple accounts |
| `URL`                    | `https://horizon.stellar.org/` | NO            | The base URL to query |

Since you can have multiple currencies on the Stellar Blockchain, all of them are exported.

Additionally, the global variables `LOGLEVEL`, `GELF_HOST`, `GELF_PORT` and `PORT` are supported.

**Note**: `TIMEOUT` is ignored.
