# blockscout.com

Support for ETH and ERC20 Tokens is implemented by querying the [blockscout.com API](https://blockscout.com/eth/mainnet/api_docs). The following environment variables are supported:

| **Variable**             | **Default**                                  | **Mandatory** | **Description**  |
|:-------------------------|:--------------------------------------------:|:-------------:|:-----------------|
| `EXCHANGE`               | -                                            | **YES**       | Set this to `blockscout` |
| `ADDRESSES`              | -                                            | **YES**       | A comma separated list of ETH addresses |
| `URL`                    | `https://blockscout.com/eth/mainnet/api`     | NO            | The base URL to query |

Additionally, the global variables `TIMEOUT`, `LOGLEVEL`, `GELF_HOST`, `GELF_PORT` and `PORT` are supported.
