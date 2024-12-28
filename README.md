# ether

<p align="center">
<img src="https://raw.githubusercontent.com/CrocoFactory/.github/main/branding/ether/bookmark.svg" height="80">
</p>
                 

[![Python versions](https://img.shields.io/pypi/pyversions/pyether?color=%234F8EE9)](https://pypi.org/project/pyether/)
[![PyPi Version](https://img.shields.io/pypi/v/pyether?color=%234F8EE9)](https://pypi.org/project/pyether/)


The web3.py operation wrapper, offering interaction through Wallet instances.

- **[Overview](#quick-overview)**
- **[Bug reports](https://github.com/CrocoFactory/ether-py/issues)**


Web3.py suggests to interact with instance of Web3 as primary entity. We offer way to use Wallet entity, that is more 
familiar, since we try to provide the similar to digital wallet apps' logic. We introduce:
 
- possibility to set and change current wallet's network by network's name
- swift and robust performing transactions
- quick performing useful functions of Web3.py

The project is made by the **[Croco Factory](https://github.com/CrocoFactory)** team
   
ether's source code is made available under the [MIT License](LICENSE)

##  Quick start
You can quickly use supported networks as RPC:  

| Network          | Native Token | Testnet |
|------------------|--------------|---------|
| Arbitrum Goerli  | ETH          | ✅       |
| Arbitrum Sepolia | ETH          | ✅       |
| Arbitrum         | ETH          | ❌       |
| Avalanche        | AVAX         | ❌       |
| Base             | ETH          | ❌       |
| Base Sepolia     | ETH          | ✅       |
| Base Goerli      | ETH          | ✅       |
| BSC              | BNB          | ❌       |
| BSC Testnet      | BNB          | ✅       |
| Ethereum         | ETH          | ❌       |
| Fantom           | FTM          | ❌       |
| Fantom Testnet   | FTM          | ✅       |
| Fuji             | AVAX         | ✅       |
| Goerli           | ETH          | ✅       |
| Linea            | ETH          | ❌       |
| Linea Goerli     | ETH          | ✅       |
| Linea Sepolia    | ETH          | ✅       |
| Mumbai           | MATIC        | ✅       |
| opBNB            | BNB          | ❌       |
| opBNB Testnet    | BNB          | ✅       |
| Optimism         | ETH          | ❌       |
| Optimism Sepolia | ETH          | ✅       |
| Optimism Goerli  | ETH          | ✅       |
| Polygon          | MATIC        | ❌       |
| Sepolia          | ETH          | ❌       |
| Scroll           | ETH          | ❌       |
| zkSync           | ETH          | ❌       |

For specifying network you only need to pass network's name.
```python
from ether import Wallet
my_wallet = Wallet('your_private_key', 'Arbitrum')
```

If you use unsupported network, you can specify it using `Network` instance
```python
from ether import Wallet, Network

network_info = Network(
    name='Custom',
    rpc='wss://custom.publicnode.com',
    token='CUSTOM'
)
custom_wallet = Wallet('your_private_key', network_info)
```

Library supports asynchronous approach
```python
from ether import AsyncWallet

async def validate_balance():
    async_wallet = AsyncWallet('your_private_key', 'Arbitrum')
    balance = await async_wallet.get_balance()
    assert balance > 0.1
```

# Installing ether

To install the package from PyPi you can use:
```shell
pip install pyether
```
        
To install the package from GitHub you can use:

```shell
pip install git+https://github.com/CrocoFactory/ether.git
```
