# ethplorer.io

Support for ETH and ERC20 Tokens is implemented by querying the [ethplorer.io API](https://ethplorer.io/). The following environment variables are supported:

| **Variable**             | **Default**                    | **Mandatory** | **Description**  |
|:-------------------------|:------------------------------:|:-------------:|:-----------------|
| `EXCHANGE`               | -                              | **YES**       | Set this to `ethplorer` |
| `API_KEY`                | `freekey`                      | NO            | Set this to your Ethplorer API key |
| `ADDRESSES`              | -                              | **YES**       | A comma separated list of ETH addresses |
| `URL`                    | `https://api.ethplorer.io`     | NO            | The base URL to query |

Additionally, the global variables `TIMEOUT`, `LOGLEVEL`, `GELF_HOST`, `GELF_PORT` and `PORT` are supported.
