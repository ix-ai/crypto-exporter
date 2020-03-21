# etherscan.io
Support for ETH and ERC20 Tokens is implemented by querying the [etherscan.io API](https://etherscan.io/apis). The following environment variables are supported:

| **Variable**             | **Default**                    | **Mandatory** | **Description**  |
|:-------------------------|:------------------------------:|:-------------:|:-----------------|
| `EXCHANGE`               | -                              | **YES**       | Set this to `etherscan` |
| `API_KEY`                | -                              | **YES**       | Set this to your Etherscan API key |
| `ADDRESSES`              | -                              | **YES**       | A comma separated list of ETH addresses |
| `TOKENS`                 | -                              | NO            | A JSON object with the list of tokens to export (see [below](#tokens-variable)) |
| `URL`                    | `https://api.etherscan.io/api` | NO            | The base URL to query |

Additionally, the global variables `TIMEOUT`, `LOGLEVEL`, `GELF_HOST`, `GELF_PORT` and `PORT` are supported.

## TOKENS Variable
Example:
```
TOKENS='[{"contract":"0x9b70740e708a083c6ff38df52297020f5dfaa5ee","name":"Daneel","short":"DAN","decimals": 10}]'
```

The technical information can be found on [etherscan.io](https://etherscan.io/token/0x9b70740e708a083c6ff38df52297020f5dfaa5ee#readContract)

**WARNING** The token balance will be retrieved for **every** address configured under `ADDRESSES`.
