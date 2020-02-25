## Off-Exchange Balances

The crypto-exporter also supports, in addition to the exchanges, reporting the account balance directly from (some) blockchains.

### ETH and ERC20 Tokens

There are two different APIs that can be used for this: [etherscan.io](https://etherscan.io/apis), [ethplorer.io](https://ethplorer.io/) and [blockscout.com](https://blockscout.com).

#### etherscan.io
Support for ETH and ERC20 Tokens is implemented by querying the [etherscan.io API](https://etherscan.io/apis). The following environment variables are supported:

| **Variable**             | **Default**                    | **Mandatory** | **Description**  |
|:-------------------------|:------------------------------:|:-------------:|:-----------------|
| `EXCHANGE`               | -                              | **YES**       | Set this to `etherscan` |
| `API_KEY`                | -                              | **YES**       | Set this to your Etherscan API key |
| `ADDRESSES`              | -                              | **YES**       | A comma separated list of ETH addresses |
| `TOKENS`                 | -                              | NO            | A JSON object with the list of tokens to export (see [below](#tokens-variable)) |
| `URL`                    | `https://api.etherscan.io/api` | NO            | The base URL to query |

Additionally, the global variables `LOGLEVEL`, `GELF_HOST`, `GELF_PORT` and `PORT` are supported.

##### TOKENS Variable
Example:
```
TOKENS='[{"contract":"0x9b70740e708a083c6ff38df52297020f5dfaa5ee","name":"Daneel","short":"DAN","decimals": 10}]'
```

The technical information can be found on [etherscan.io](https://etherscan.io/token/0x9b70740e708a083c6ff38df52297020f5dfaa5ee#readContract)

**WARNING** The token balance will be retrieved for **every** address configured under `ADDRESSES`.

#### ethplorer.io

Support for ETH and ERC20 Tokens is implemented by querying the [ethplorer.io API](https://ethplorer.io/). The following environment variables are supported:

| **Variable**             | **Default**                    | **Mandatory** | **Description**  |
|:-------------------------|:------------------------------:|:-------------:|:-----------------|
| `EXCHANGE`               | -                              | **YES**       | Set this to `ethplorer` |
| `API_KEY`                | `freekey`                      | NO            | Set this to your Ethplorer API key |
| `ADDRESSES`              | -                              | **YES**       | A comma separated list of ETH addresses |
| `URL`                    | `https://api.ethplorer.io`     | NO            | The base URL to query |

Additionally, the global variables `LOGLEVEL`, `GELF_HOST`, `GELF_PORT` and `PORT` are supported.

#### blockscout.com

Support for ETH and ERC20 Tokens is implemented by querying the [blockscout.com API](https://blockscout.com/eth/mainnet/api_docs). The following environment variables are supported:

| **Variable**             | **Default**                                  | **Mandatory** | **Description**  |
|:-------------------------|:--------------------------------------------:|:-------------:|:-----------------|
| `EXCHANGE`               | -                                            | **YES**       | Set this to `blockscout` |
| `ADDRESSES`              | -                                            | **YES**       | A comma separated list of ETH addresses |
| `URL`                    | `https://blockscout.com/eth/mainnet/api`     | NO            | The base URL to query |

Additionally, the global variables `LOGLEVEL`, `GELF_HOST`, `GELF_PORT` and `PORT` are supported.

### BTC
Support for the BTC account balance is implemented by querying the [blockchain.info API](https://www.blockchain.com/api). The following environment variables are supported:

| **Variable**             | **Default**               | **Mandatory** | **Description**  |
|:-------------------------|:-------------------------:|:-------------:|:-----------------|
| `EXCHANGE`               | -                         | **YES**       | Set this to `blockchain` |
| `ADDRESSES`              | -                         | **YES**       | A comma separated list of BTC addresses |
| `URL`                    | `https://blockchain.info` | NO            | The base URL to query |

Additionally, the global variables `LOGLEVEL`, `GELF_HOST`, `GELF_PORT` and `PORT` are supported.

### Ripple
Support for the Ripple account balance is implemented by querying the [ripple.com API](https://data.ripple.com). The following environment variables are supported:

| **Variable**             | **Default**               | **Mandatory** | **Description**  |
|:-------------------------|:-------------------------:|:-------------:|:-----------------|
| `EXCHANGE`               | -                         | **YES**       | Set this to `ripple` |
| `ADDRESSES`              | -                         | **YES**       | A comma separated list of Ripple accounts |
| `URL`                    | `https://data.ripple.com` | NO            | The base URL to query |

Since you can have multiple currencies on the Ripple Blockchain, all of them are exported.

Additionally, the global variables `LOGLEVEL`, `GELF_HOST`, `GELF_PORT` and `PORT` are supported.

### Stellar
Support for the Stellar account balance is implemented by querying the [stellar horizon server](https://horizon.stellar.org/). The following environment variables are supported:

| **Variable**             | **Default**                    | **Mandatory** | **Description**  |
|:-------------------------|:------------------------------:|:-------------:|:-----------------|
| `EXCHANGE`               | -                              | **YES**       | Set this to `stellar` |
| `ADDRESSES`              | -                              | **YES**       | A comma separated list of Ripple accounts |
| `URL`                    | `https://horizon.stellar.org/` | NO            | The base URL to query |

Since you can have multiple currencies on the Stellar Blockchain, all of them are exported.

Additionally, the global variables `LOGLEVEL`, `GELF_HOST`, `GELF_PORT` and `PORT` are supported.
