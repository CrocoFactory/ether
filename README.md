# ether

<p align="center">
<img src="https://raw.githubusercontent.com/CrocoFactory/.github/main/branding/ether/bookmark.svg" height="80">
</p>
                 

[![Python versions](https://img.shields.io/pypi/pyversions/pyether?color=%234F8EE9)](https://pypi.org/project/pyether/)
[![PyPi Version](https://img.shields.io/pypi/v/pyether?color=%234F8EE9)](https://pypi.org/project/pyether/)


The package, containing wrapper over web3.py operations for interacting through Wallet entities.

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
     
<h2 id="quick-overview">Quick overview</h2> 
You can perform the following actions, using ether:

- **[approve](#approve)**
- **[build_and_transact](#build_and_transact)**
- **[build_tx_params](#build_tx_params)**
- **[create](#create)**
- **[estimate_gas](#estimate_gas)**
- **[get_balance](#get_balance)**
- **[get_balance_of](#get_balance_of)**
- **[get_token](#get_token)**
- **[get_explorer_url](#get_explorer_url)**
- **[is_native_token](#is_native_token)**
- **[transact](#transact)**
- **[transfer](#transfer)**

<h3 id="approve">approve</h3>

When you want to spend non-native tokens, for instance USDT, you need to perform approving operation.

```python
from ether import Wallet
my_wallet = Wallet('your_private_key', 'Arbitrum')
provider = my_wallet.provider

stargate_router = '0x8731d54E9D02c286767d56ac03e8037C07e01e98'
usdt = my_wallet.get_token('0xdAC17F958D2ee523a2206206994597C13D831ec7')
usdt_amount = provider.to_wei(0.001, 'ether')

my_wallet.approve(usdt, stargate_router, usdt_amount)
```

<h3 id="build_and_transact">build_and_transact</h3>
If you don't need to check estimated gas or directly use transact, you can call build_and_transact. It's based on getting
closure as argument. Closure is transaction's function, called with arguments. Notice that it has to be not built or 
awaited

```python
from ether import Wallet
my_wallet = Wallet('your_private_key', 'Arbitrum')
provider = my_wallet.provider

stargate_abi = [...]
stargate_router = '0x8731d54E9D02c286767d56ac03e8037C07e01e98'
stargate = my_wallet.provider.eth.contract(stargate_router, abi=stargate_abi)

eth_amount = provider.to_wei(0.001, 'ether')
closure = stargate.functions.swapETH(...) 
my_wallet.build_and_transact(closure, eth_amount)
```

<h3 id="build_tx_params">build_tx_params</h3>
You can use build_tx_params to quickly get dictionary of params for building transaction. Public key, chain id 
and nonce are generated automatically. You also can also choose not to set a gas and the gas price

```python
from ether import Wallet
my_wallet = Wallet('your_private_key', 'BSC')

my_wallet.build_tx_params(0)
```

```json
{
  "from": "0xe977Fa8D8AE7D3D6e28c17A868EF04bD301c583f", 
  "chainId": 56, 
  "nonce": 168, 
  "value": 0, 
  "gas": 250000, 
  "gasPrice": 1000000000
}
```

<h3 id="create">create</h3>
You can use that, when you want to create all-new wallet

```python
from ether import Wallet
wallet = Wallet.create('Arbitrum')
```
            
<h3 id="estimate_gas">estimate_gas</h3>
When you want to estimate an amount of gas to send a transaction, you can use estimate_gas

```python
from ether import Wallet

my_wallet = Wallet('your_private_key', 'Arbitrum')
provider = my_wallet.provider

stargate_router = '0x8731d54E9D02c286767d56ac03e8037C07e01e98'
stargate_abi = [...]
eth_amount = provider.to_wei(0.001, 'ether')

stargate = my_wallet.provider.eth.contract(stargate_router, abi=stargate_abi)
params = my_wallet.build_tx_params(eth_amount)
tx_params = stargate.functions.swapETH(...).buildTransaction(params)
gas = my_wallet.estimate_gas(tx_params)
tx_params['gas'] = gas

my_wallet.transact(tx_params)
```

<h3 id="get_balance">get_balance</h3>
You can get the balance of the native token of your wallet.

```python
from ether import Wallet
my_wallet = Wallet('your_private_key', 'Arbitrum')
balance = my_wallet.get_balance()
```

<h3 id="get_balance_of">get_balance_of</h3>
You can get the balance of specified token of your wallet

```python
from ether import Wallet
my_wallet = Wallet('your_private_key', 'Arbitrum')

usdt = my_wallet.get_token('0xdAC17F958D2ee523a2206206994597C13D831ec7')
balance = my_wallet.get_balance_of(usdt, convert=True)
print(balance)
```

<h3 id="get_token">get_token</h3>
You can get the `Token` instance, containing information about symbol and decimals. Also this function used for 
another instance-methods of Wallet.

```python
from ether import Wallet
my_wallet = Wallet('your_private_key', 'Arbitrum')
usdt = my_wallet.get_token('0xdAC17F958D2ee523a2206206994597C13D831ec7')
print(usdt.decimals)
```
            
<h3 id="get_explorer_url">get_explorer_url</h3>
You can get entire wallet's list of transactions

```python
from ether import Wallet
from web3.contract import Contract
my_wallet = Wallet('your_private_key', 'Arbitrum')
provider = my_wallet.provider

stargate_router = '0x8731d54E9D02c286767d56ac03e8037C07e01e98'
stargate_abi = [...]
stargate = Contract(stargate_router, stargate_abi)

eth_amount = provider.to_wei(0.001, 'ether')
closure = stargate.functions.swapETH(...) 
tx_hash = my_wallet.build_and_transact(closure, eth_amount)
print(my_wallet.get_explorer_url(tx_hash))
```

<h3 id="is_native_token">is_native_token</h3>
If you want to check, if the specific token is native token of network, you can use is_native_token.

You can use any case in a token's ticker.
```python
from ether import Wallet
my_wallet = Wallet('your_private_key', 'Arbitrum')
assert my_wallet.is_native_token('eTh')
```

<h3 id="transact">transact</h3>
After building transaction you can perform it, passing transaction data to transact

```python
from ether import Wallet

my_wallet = Wallet('your_private_key', 'Arbitrum')
provider = my_wallet.provider

stargate_router = '0x8731d54E9D02c286767d56ac03e8037C07e01e98'
stargate_abi = [...]
eth_amount = provider.to_wei(0.001, 'ether')

stargate = my_wallet.provider.eth.contract(stargate_router, abi=stargate_abi)
params = my_wallet.build_tx_params(eth_amount)
tx_data = stargate.functions.swapETH(...).buildTransaction(params)
gas = my_wallet.estimate_gas(tx_data)
tx_data['gas'] = gas

my_wallet.transact(tx_data)
```

<h3 id="transfer">transfer</h3>
You can transfer tokens to another wallet

```python
from ether import Wallet
my_wallet = Wallet('your_private_key', 'Arbitrum')
provider = my_wallet.provider

recipient = '0xe977Fa8D8AE7D3D6e28c17A868EF04bD301c583f'
usdt = my_wallet.get_token('0xdAC17F958D2ee523a2206206994597C13D831ec7')
usdt_amount = provider.to_wei(0.001, 'ether')

my_wallet.transfer(usdt, recipient, usdt_amount)
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
