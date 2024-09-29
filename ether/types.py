from pydantic import BaseModel, HttpUrl, field_validator, PositiveInt
from web3.types import Wei
from eth_typing import Address, HexAddress,  ChecksumAddress
from typing import Union

from ether.utils import is_checksum_address

TokenAmount = Union[Wei, int]
AnyAddress = Union[Address, HexAddress, ChecksumAddress, bytes, str]


class Token(BaseModel):
    address: ChecksumAddress
    symbol: str
    decimals: int

    @field_validator('address')
    def _validate_address(cls, value):
        if not is_checksum_address(value):
            raise ValueError(f"Address {value} is not a valid checksum address")
        return value


class Network(BaseModel):
    name: str
    rpc: str
    token: str
    chain_id: Union[PositiveInt, None] = None
    explorer: Union[HttpUrl, None] = None

    @field_validator('rpc', 'explorer')
    def _validate_rpc(cls, value):
        HttpUrl(value)
        return str(value)
