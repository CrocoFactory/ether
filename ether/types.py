from pydantic import BaseModel, HttpUrl, field_validator, PositiveInt
from web3.types import Wei
from eth_typing import Address, HexAddress,  ChecksumAddress
from typing import Union, TypeAlias
from ether.utils import is_checksum_address

TokenAmount: TypeAlias = Union[Wei, int]
AnyAddress: TypeAlias = Union[Address, HexAddress, ChecksumAddress, bytes, str]


class Token(BaseModel):
    """
    The Token class represents an ERC-20 token.

    Attributes:
        address: The address of the token contract.
        symbol: The token's symbol (e.g., "ETH", "USDT").
        decimals: The number of decimal places the token supports.

    Example:
        ```python
        from ether import Wallet

        wallet = Wallet('0xPrivateKey', 'Ethereum')

        # Token details
        token_address = '0xTokenAddressHere'
        token = wallet.get_token(token_address)

        print(f"Token {token.symbol} is loaded!")
        ```
    """

    address: ChecksumAddress
    symbol: str
    decimals: int

    @field_validator('address')
    def _validate_address(cls, value):
        if not is_checksum_address(value):
            raise ValueError(f"Address {value} is not a valid checksum address")
        return value


class Network(BaseModel):
    """
    The Network class represents an Ethereum-based network configuration.

    Attributes:
        name: The name of the network (e.g., "Ethereum", "Arbitrum").
        rpc: The RPC URL for interacting with the network.
        token: The network's native token (e.g., "ETH", "BNB").
        chain_id: The chain ID for the network. If not provided, it will be added automatically, when passing network to wallet.
        explorer: The URL for the blockchain explorer.

    Example:
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
    """
    name: str
    rpc: str
    token: str
    chain_id: Union[PositiveInt, None] = None
    explorer: Union[HttpUrl, None] = None

    @field_validator('rpc', 'explorer')
    def _validate_rpc(cls, value):
        HttpUrl(value)
        return str(value)
