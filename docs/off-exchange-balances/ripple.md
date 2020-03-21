# Ripple
Support for the Ripple account balance is implemented by querying the [ripple.com API](https://data.ripple.com). The following environment variables are supported:

| **Variable**             | **Default**               | **Mandatory** | **Description**  |
|:-------------------------|:-------------------------:|:-------------:|:-----------------|
| `EXCHANGE`               | -                         | **YES**       | Set this to `ripple` |
| `ADDRESSES`              | -                         | **YES**       | A comma separated list of Ripple accounts |
| `URL`                    | `https://data.ripple.com` | NO            | The base URL to query |

Since you can have multiple currencies on the Ripple Blockchain, all of them are exported.

Additionally, the global variables `TIMEOUT`, `LOGLEVEL`, `GELF_HOST`, `GELF_PORT` and `PORT` are supported.
