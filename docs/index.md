# ether
<a href="https://pypi.org/project/pyether/">
<h1 align="center">
<img alt="Logo Banner" src="https://raw.githubusercontent.com/CrocoFactory/.github/main/branding/ether/bookmark.svg" width="300">
</h1><br>
</a>

*The python package for interacting with Ethereum.*

[![Python versions](https://img.shields.io/pypi/pyversions/pyether?color=%234F8EE9)](https://pypi.org/project/pyether/)
[![PyPi Version](https://img.shields.io/pypi/v/pyether?color=%234F8EE9)](https://pypi.org/project/pyether/)

---

**Documentation:** [https://ether.crocofactory.dev](https://ether.crocofactory.dev)

**Source code:** [https://github.com/CrocoFactory/ether](https://github.com/CrocoFactory/ether)

---
         

`ether` is a Python library designed to interact with the Ethereum blockchain, providing a simple and intuitive way to work with Ethereum accounts, transactions, smart contracts, and tokens. It is a wrapper around the popular `web3.py` library, making Ethereum interaction easier for developers.

With `ether`, you can:

- 🔑 **Manage Accounts**: Easily generate wallet objects using your private key and interact with various Ethereum networks (e.g., Arbitrum, Polygon, BSC).  
- 💰 **Check balances**: Retrieve the balance of your Ethereum account and manage funds across different chains.  
- 🚀 **Make transactions**: Transfer Ether and ERC-20 tokens seamlessly between Ethereum accounts.  
- 💥 **Smart contracts**: Call functions and send transactions to Ethereum smart contracts, enabling interaction with DeFi protocols and decentralized applications (dApps).  
- 🔗 **Easily integrate chains**: Seamlessly add and interact with custom Ethereum networks by name or through a `Network` object, making it simple to connect with various blockchain environments.     
- ⚡ **Asynchronous support**: Perform network calls asynchronously, ideal for working in applications that require non-blocking behavior.
       

...and much more. Unlock a wide range of functionalities to simplify Ethereum development, enhance your dApp experience, and seamlessly integrate blockchain operations into your projects.


Table of Contents:

1. [Quick Overview](#quick-overview)
2. [First Transaction](#first-transaction)
2. [Comparison](#comparison)
4. [Installing](#installing)

## Quick Overview

Each Ethereum account has the associated:

- **Public Key** 🔑 (32 bytes, 66 characters): synonym for account address. You use it when you want to share payment details. 
- **Private Key** 🔐 (20 bytes, 42 characters): key required for making (signing) transactions. It's like a **password**, but stronger. You should not 
  share it with others. 

You can make transactions in different networks (chains), like:

- Arbitrum
- Base
- BSC
- Ethereum
- Optimism
- Polygon
- zkSync

They can differ from each other by some criteria, like native token and average transaction fees (gas ⛽). To interact with 
some chain, you have to connect to its RPC. 


## First Transaction

Before making transactions, you need to create an object, associated with your Ethereum account. This object is called `Wallet`.
```python
from ether import Wallet
my_wallet = Wallet('0xPrivateKey', 'Arbitrum')
```

The first argument is private key. The second is network, represented as `Network` object or network's name, if you use one of 
the built-innetworks.

Example with `Network` instance:

```python
from ether import Wallet, Network

network = Network(
  name='BOB', 
  rpc='https://bob.drpc.org', 
  token='ETH', 
  explorer='https://explorer.gobob.xyz'
)

custom_wallet = Wallet('0xPrivateKey', network)
```

Furthermore, `ether` supports asynchronous approach:

```python
from ether import AsyncWallet

async def validate_balance():
    async_wallet = AsyncWallet('0xPrivateKey', 'Arbitrum')
    balance = await async_wallet.get_balance()
    assert balance > 0.1
```

Once your wallet is created, you can perform transactions easily. Let's start with a simple Ethereum transfer from your 
wallet to another address.

```python
from ether import Wallet

# Create a wallet instance
wallet = Wallet('0xPrivateKey', 'Ethereum')

# Define the recipient address and amount to send
recipient = '0xRecipientAddressHere'
amount_in_wei = 10 ** 18  # 1 Ether (in Wei units)

# Perform the transfer
params = wallet.build_tx_params(amount_in_wei, recipient)
tx_hash = wallet.transact(params)

print(f"Transaction sent! Hash: {params.hex()}")
```

### Contract Calls

Interacting with smart contracts is seamless with `ether`. 

```python
from ether import Wallet

# Initialize the wallet object with your private key and network (e.g., Arbitrum)
wallet = Wallet('0xPrivateKey', 'Arbitrum')

# Access the provider associated with the wallet
provider = wallet.provider

# Define the ABI (Application Binary Interface) of the smart contract and the contract address
stargate_abi = [...]  
stargate_router = '0x8731d54E9D02c286767d56ac03e8037C07e01e98'  # Contract address (Stargate Router)

# Create a contract instance using the ABI and contract address
stargate = wallet.provider.eth.contract(address=stargate_router, abi=stargate_abi)

usdt = '0xUsdtAddress'  
eth_amount = provider.to_wei(0.001, 'ether')  # 0.001 Ether to Wei

# Prepare the contract function call to swap ETH for USDT using the smart contract's function
closure = stargate.functions.swapETH(eth_amount, usdt)

# Build the transaction and send it
wallet.build_and_transact(closure, eth_amount)
```

### Sending Tokens 

To send ERC-20 tokens, use the `transfer` method with the token contract address and recipient details:

```python
from ether import Wallet

wallet = Wallet('0xPrivateKey', 'Ethereum')

# Token details
token_address = '0xTokenAddressHere'
token = wallet.get_token(token_address)

# Recipient and amount
recipient = '0xRecipientAddressHere'
amount = 100 * 10 ** token.decimals  # Sending 100 USDT

# Perform the token transfer
transaction_hash = wallet.transfer(token, recipient, amount)

print(f"Token transfer sent! Hash: {transaction_hash.hex()}")
```

### Approving Tokens

If you plan to interact with DeFi protocols, you might need to approve a contract to spend your tokens:

```python
# Contract address (e.g., a DeFi protocol)
contract_address = '0xContractAddressHere'
amount_to_approve = 1000 * 10 ** token.decimals

# Approve the contract to spend tokens
approval_tx_hash = wallet.approve(token, contract_address, amount_to_approve)

print(f"Approval transaction sent! Hash: {approval_tx_hash.hex()}")
```

### Utility Functions

- `get_balance(from_wei=False)`: Retrieves the account balance. Use `from_wei=True` to get the balance in Ether units.

    ```python
    balance = wallet.get_balance(from_wei=True)
    print(f"Current balance: {balance} ETH")
    ```

- `estimate_gas(tx_params)`: Estimates the gas required for a transaction.

    ```python
    estimated_gas = wallet.estimate_gas({
        'to': recipient,
        'value': amount_in_wei
    })
    print(f"Estimated gas: {estimated_gas}")
    ```      

By following these examples, you can start interacting with Ethereum and tokens using `ether`. For further details, explore the full documentation linked above.
                
## Comparison

`ether` simplifies many Ethereum-related tasks by abstracting common operations and reducing the amount of boilerplate
code required in `web3.py`.

### `web3.py`

To send Ether using `web3.py`, you would need to build the transaction manually, estimate gas, and sign it:

```python
from web3 import Web3

# Initialize Web3 instance
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/...'))

# Sender and recipient details
sender_address = '0xSenderAddressHere'
recipient_address = '0xRecipientAddressHere'
private_key = '0xPrivateKey'

# Get nonce (transaction count)
nonce = w3.eth.get_transaction_count(sender_address)

# Prepare transaction details
tx = {
    'to': recipient_address,
    'value': w3.to_wei(0.1, 'ether'),  # Sending 0.1 Ether
    'gas': 2000000,
    'gasPrice': w3.to_wei('20', 'gwei'),
    'nonce': nonce,
}

# Sign the transaction
signed_tx = w3.eth.account.sign_transaction(tx, private_key)

# Send the transaction
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

print(f"Transaction sent! Hash: {tx_hash.hex()}")
```

### `ether`

With `ether`, the same operation is simplified to 2 method calls:

```python
from ether import Wallet

# Create a wallet instance
wallet = Wallet('0xPrivateKey', 'Ethereum')

# Define recipient and amount
recipient = '0xRecipientAddressHere'
amount_in_wei = 10 ** 18  # 1 Ether (in Wei)

# Build transaction params and send the transaction
params = wallet.build_tx_params(amount_in_wei, recipient)
tx_hash = wallet.transact(params)

print(f"Transaction sent! Hash: {tx_hash.hex()}")
```


## Installing
To install `ether` from PyPi, you can use that:

```shell
pip install pyether
```

To install `ether` from GitHub, use that:

```shell
pip install git+https://github.com/CrocoFactory/ether.git
```