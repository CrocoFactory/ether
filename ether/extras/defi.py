from abc import ABC
from typing import Optional, Union
from web3 import AsyncWeb3, Web3
from ether import AsyncWallet, Network, Wallet
from typing import TypeVar


WalletT = TypeVar('WalletT', AsyncWallet, Wallet)


class Defi(ABC):
    """
    Abstract base class for implementing classes interacting decentralized finance (DeFi) protocols.

    Args:
        wallet: An instance of ether.AsyncWallet or ether.Wallet.
        name:  Name of the specific DeFi.
        version: Optional version number of the DeFi protocol
    """

    def __init__(
            self,
            wallet: WalletT,
            name: str,
            version: Optional[int] = None
    ):
        self.__wallet = wallet
        self._network = wallet.network
        self._name = name
        self._version = version

    @property
    def wallet(self) -> WalletT:
        """The wallet instance associated with this DeFi instance."""
        return self.__wallet

    @property
    def network(self) -> Network:
        """Current network of Defi represented as [`Network`][ether.Network] instance"""
        return self._network

    @property
    def provider(self) -> Union[Web3, AsyncWeb3]:
        """Gets the AsyncWeb3/Web3 provider associated with the wallet instance."""
        return self.wallet.provider

    @property
    def version(self) -> Optional[int]:
        """The version number of the DeFi protocol."""
        return self._version
