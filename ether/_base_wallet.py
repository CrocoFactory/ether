from __future__ import annotations

import os
import json
from functools import lru_cache
from typing_extensions import Self
from typing import ClassVar, Optional
from eth_account import Account
from eth_typing import ChecksumAddress, HexStr
from abc import ABC, abstractmethod
from hexbytes import HexBytes
from web3 import AsyncWeb3, Web3
from web3.contract.contract import ContractFunction, Contract
from web3.contract.async_contract import AsyncContract, AsyncContractFunction
from web3.types import ABI, Wei, TxParams
from ether.types import Network, AnyAddress, TokenAmount, Token


class _BaseWallet(ABC):
    __networks = [
        Network(
            name='Arbitrum Sepolia',
            chain_id=421614,
            rpc='https://arbitrum-sepolia-rpc.publicnode.com',
            token='ETH',
            explorer='https://sepolia.arbiscan.io'
        ),
        Network(
            name='Arbitrum',
            chain_id=42161,
            rpc='https://arbitrum-one-rpc.publicnode.com',
            token='ETH',
            explorer='https://arbiscan.io'
        ),
        Network(
            name='Avalanche',
            chain_id=43114,
            rpc='https://avalanche-c-chain-rpc.publicnode.com',
            token='AVAX',
            explorer='https://snowtrace.io/'
        ),
        Network(
            name='Base',
            chain_id=8453,
            rpc='https://base-rpc.publicnode.com',
            token='ETH',
            explorer='https://basescan.org/'
        ),
        Network(
            name='Base Goerli',
            chain_id=84531,
            rpc='https://base-goerli.public.blastapi.io',
            token='ETH',
            explorer='https://goerli.basescan.org/'
        ),
        Network(
            name='Base Sepolia',
            chain_id=84532,
            rpc='https://base-sepolia-rpc.publicnode.com',
            token='ETH',
            explorer='https://sepolia.basescan.org/'
        ),
        Network(
            name='BSC',
            chain_id=56,
            rpc='https://bsc-rpc.publicnode.com',
            token='BNB',
            explorer='https://bscscan.com'
        ),
        Network(
            name='BSC Testnet',
            chain_id=97,
            rpc='https://bsc-testnet-rpc.publicnode.com',
            token='BNB',
            explorer='https://testnet.bscscan.com'
        ),
        Network(
            name='Ethereum',
            chain_id=1,
            rpc='https://ethereum-rpc.publicnode.com',
            token='ETH',
            explorer='https://etherscan.io'
        ),
        Network(
            name='Fantom',
            chain_id=250,
            rpc='https://fantom-rpc.publicnode.com',
            token='FTM',
            explorer='https://ftmscan.com/'
        ),
        Network(
            name='Fantom Testnet',
            chain_id=4002,
            rpc='https://fantom-testnet-rpc.publicnode.com',
            token='FTM',
            explorer='https://testnet.ftmscan.com/'
        ),
        Network(
            name='Fuji',
            chain_id=43113,
            rpc='https://avalanche-fuji-c-chain-rpc.publicnode.com',
            token='AVAX',
            explorer='https://testnet.snowtrace.io'
        ),
        Network(
            name='Goerli',
            chain_id=5,
            rpc='https://goerli.gateway.tenderly.co',
            token='ETH',
            explorer='https://goerli.etherscan.io'
        ),
        Network(
            name='Linea',
            chain_id=59144,
            rpc='https://linea.drpc.org',
            token='ETH',
            explorer='https://lineascan.build/'
        ),
        Network(
            name='Linea Goerli',
            chain_id=59140,
            rpc='https://linea-goerli.drpc.org',
            token='ETH',
            explorer='https://goerli.lineascan.build/'
        ),
        Network(
            name='Mumbai',
            chain_id=80001,
            rpc='https://polygon-mumbai-bor-rpc.publicnode.com',
            token='MATIC',
            explorer='https://mumbai.polygonscan.com/'
        ),
        Network(
            name='opBNB',
            chain_id=204,
            rpc='https://opbnb-rpc.publicnode.com',
            token='BNB',
            explorer='https://opbnb.bscscan.com/'
        ),
        Network(
            name='opBNB Testnet',
            chain_id=5611,
            rpc='https://opbnb-testnet-rpc.publicnode.com',
            token='BNB',
            explorer='https://opbnb-testnet.bscscan.com'
        ),
        Network(
            name='Optimism',
            chain_id=10,
            rpc='https://optimism-rpc.publicnode.com',
            token='ETH',
            explorer='https://optimistic.etherscan.io'
        ),
        Network(
            name='Optimism Sepolia',
            chain_id=11155420,
            rpc='https://optimism-sepolia-rpc.publicnode.com',
            token='ETH',
            explorer='https://sepolia-optimism.etherscan.io/'
        ),
        Network(
            name='Optimism Goerli',
            chain_id=420,
            rpc='https://optimism-testnet.drpc.org',
            token='ETH',
            explorer='https://goerli-optimism.etherscan.io'
        ),
        Network(
            name='Polygon',
            chain_id=137,
            rpc='https://polygon-bor-rpc.publicnode.com',
            token='MATIC',
            explorer='https://polygonscan.com'
        ),
        Network(
            name='Sepolia',
            chain_id=11155111,
            rpc='https://ethereum-sepolia-rpc.publicnode.com',
            token='ETH',
            explorer='https://sepolia.etherscan.io'
        ),
        Network(
            name='Scroll',
            chain_id=534352,
            rpc='https://scroll.drpc.org',
            token='ETH',
            explorer='https://scrollscan.com'
        ),
        Network(
            name='zkSync',
            chain_id=324,
            rpc='https://zksync.drpc.org',
            token='ETH',
            explorer='https://explorer.zksync.io'
        )
    ]

    __network_map: ClassVar[dict[str, Network]] = {network.name: network for network in __networks}

    def __init__(
            self,
            private_key: str,
            network: Network | str,
            is_async: bool = False
    ):
        self.__is_async = is_async
        self.__account = Account.from_key(private_key)
        self.__private_key = private_key
        self.__public_key = Web3.to_checksum_address(self.__account.address)
        self.network = network

    @classmethod
    def create(cls, network: Network | str = 'Ethereum') -> Self:
        """
        Creates a new ethereum account and associated Wallet | AsyncWallet instance.

        Args:
            network: The name of the built-in Ethereum-based network or custom network configuration

        Returns:
            Self: Instance of Wallet | AsyncWallet.
        """
        private_key = Account.create().key
        return cls(private_key, network)

    @property
    def provider(self) -> AsyncWeb3 | Web3:
        """
        Gets the provider instance.

        Returns:
            AsyncWeb3 | Web3: The provider (synchronous or asynchronous).
        """
        return self._provider

    @property
    def network(self) -> Network:
        """
        Gets the current [Network][ether.Network] instance.

        Returns:
            Network: The current network instance.
        """
        return self._network

    @network.setter
    def network(self, value: Network | str) -> None:
        """
        Sets the [Network][ether.Network] of the wallet.

        Args:
            value: Name of built-innetwork or a custom network configuration.
        """
        is_async = self.__is_async

        if isinstance(value, Network):
            value = value.model_copy()

        network = self.__validate_network(value)
        rpc = network.rpc

        temp_provider = Web3(Web3.HTTPProvider(rpc))
        self.__validate_chain_id(network, temp_provider)

        if is_async:
            self._provider = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc))
        else:
            self._provider = temp_provider

        self._nonce = temp_provider.eth.get_transaction_count(self.__public_key)
        self._network = network

    @property
    def private_key(self) -> str:
        """
        Returns the account's key required for making (signing) transactions.

        Returns:
            str: Account's key required for making (signing) transactions.
        """
        return self.__private_key

    @property
    def public_key(self) -> ChecksumAddress:
        """
        Returns the account's key used for sharing payment details.

        Returns:
            ChecksumAddress: The account's key used for sharing payment details.
        """
        return self.__public_key

    @property
    def nonce(self) -> int:
        """
        Returns the account's overall number of transactions.

        Returns:
            int: Account's overall number of transactions.
        """
        return self._nonce

    @property
    def native_token(self) -> str:
        """
        Gets the native token of the current network.

        Returns:
            str: The native token of the current network.
        """
        return self.network.token

    @classmethod
    def network_map(cls) -> dict[str, Network]:
        """
        Returns a copy of the network map, containing information about built-in networks.

        Returns:
            dict[str, Network]: The network map.
        """
        return cls.__network_map.copy()

    def is_native_token(self, token: str) -> bool:
        """
        Checks if the token is the native token of the network.

        Args:
            token: Token symbol.

        Returns:
            bool: True if the token is native, False otherwise.
        """
        network = self.network

        native_token = network.token
        return token.upper() == native_token or token.lower() == native_token

    @classmethod
    def __validate_network(
            cls,
            network: Network | str
    ) -> Network:
        """
        Validates the network.

        Args:
            network (Network | str): Network or name of the network.

        Returns:
            Network: The validated network.
        """
        mapping = cls.__network_map
        if isinstance(network, str) and network in mapping.keys():
            network = mapping[network]
        elif not isinstance(network, Network):
            raise TypeError(f"Network must be a {Network} object or name of a built-in "
                            f"network. Actual type: {type(network)}")

        return network

    @classmethod
    def __validate_chain_id(cls, network: Network, provider: Web3) -> Network:
        """
        Validates the chain ID of the network.

        Args:
            network (Network): The network object.
            provider (Web3): Web3 provider instance.

        Returns:
            Network: The network with validated chain ID.
        """
        chain_id = provider.eth.chain_id
        if network.chain_id is not None and chain_id != network.chain_id:
            raise ValueError(f'Chain id of {Network} info must be equal to the actual chain`s id. Try to find it by: '
                             f'https://chainlist.org/?search={network.name.lower()}')
        else:
            network.chain_id = chain_id

        return network

    @staticmethod
    @lru_cache()
    def _get_erc20_abi() -> ABI:
        """
        Loads the ERC-20 ABI.

        Returns:
            ABI: The ERC-20 ABI.
        """
        abs_path = os.path.dirname(os.path.abspath(__file__))
        path = f"{abs_path}/erc20.abi"
        with open(path) as file:
            return json.load(file)

    @lru_cache(maxsize=6)
    def _load_token_contract(self, address: AnyAddress, abi: ABI | None = None) -> AsyncContract | Contract:
        """
        Loads the token contract for the specified address.

        Args:
            address (AnyAddress): Token address.
            abi (ABI | None, optional): Contract ABI. Defaults to USDT ABI.

        Returns:
            AsyncContract | Contract: The token contract.
        """
        if isinstance(address, bytes):
            address = address.hex()

        provider = self.provider
        address = provider.to_checksum_address(address)

        if not abi:
            abi = self._get_erc20_abi()

        contract = provider.eth.contract(address=address, abi=abi)
        return contract

    def get_explorer_url(self, tx_hash: HexBytes | str) -> str:
        """
        Returns the explorer URL for the given transaction hash.

        Args:
            tx_hash: Transaction hash.

        Returns:
            str: Explorer URL for the transaction.
        """
        if isinstance(tx_hash, bytes):
            tx_hash = tx_hash.hex()
        elif not isinstance(tx_hash, str):
            raise TypeError(f"Invalid transaction hash type. Hash must be a `bytes` object or `str`. "
                            f"Actual type:  {type(tx_hash)}")

        explorer_url = f'{self.network.explorer}/tx/{tx_hash}'
        return explorer_url

    @abstractmethod
    def get_token(self, address: AnyAddress, abi: ABI | None = None) -> Token:
        """
        Retrieves token information for the specified address.

        Args:
            address (AnyAddress): Token address.
            abi (ABI | None, optional): Contract ABI. Defaults to USDT ABI.

        Returns:
            Token: Token object.
        """
        pass

    @abstractmethod
    def get_balance(self, from_wei: bool = False) -> float | Wei:
        """
        Retrieves the balance of the wallet.

        Args:
            from_wei (bool): Whether to convert the balance from Wei to Ether.

        Returns:
            float | Wei: Balance of the wallet.
        """
        pass

    @abstractmethod
    def estimate_gas(self, tx_params: TxParams, from_wei: bool = False) -> Wei:
        """
        Estimates the gas cost for the transaction.

        Args:
            tx_params (TxParams): Transaction parameters.
            from_wei (bool): Whether to convert gas from Wei.

        Returns:
            Wei: Gas estimate.
        """
        pass

    @abstractmethod
    def build_and_transact(
            self,
            closure: ContractFunction | AsyncContractFunction,
            value: TokenAmount = 0,
            gas: Optional[int] = None,
            max_fee: Wei | None = None,
            max_priority_fee: Wei | None = None,
            validate_status: bool = False
    ) -> HexBytes:
        """
        Builds and executes a transaction.

        Args:
            closure (ContractFunction | AsyncContractFunction): Contract function.
            value (TokenAmount, optional): Transaction value. Defaults to 0.
            gas (Optional[int], optional): Gas limit. Defaults to None.
            max_fee (Wei, optional): The maximum fee per gas. Defaults to None.
            max_priority_fee: (Wei, optional) The maximum priority fee per gas. Defaults to None.
            validate_status (bool, optional): Whether to validate the transaction status. Defaults to False.

        Returns:
            HexBytes: Transaction hash.
        """
        pass

    @abstractmethod
    def approve(
            self,
            token: Token,
            contract_address: AnyAddress,
            token_amount: TokenAmount,
            gas: Optional[int] = None,
            max_fee: Wei | None = None,
            max_priority_fee: Wei | None = None,
            validate_status: bool = False
    ) -> HexBytes:
        """
        Approves a specified amount of tokens for a contract.

        Args:
            token (Token): Token object.
            contract_address (AnyAddress): Contract address.
            token_amount (TokenAmount): Amount of tokens to approve.
            gas (Optional[int], optional): Gas limit. Defaults to None.
            max_fee (Wei, optional): The maximum fee per gas. Defaults to None.
            max_priority_fee: (Wei, optional) The maximum priority fee per gas. Defaults to None.
            validate_status (bool, optional): Whether to validate the transaction status. Defaults to False.

        Returns:
            HexBytes: Transaction hash.
        """
        pass

    @abstractmethod
    def build_tx_params(
            self,
            value: TokenAmount,
            recipient: Optional[AnyAddress] = None,
            raw_data: Optional[bytes | HexStr] = None,
            gas: Wei = Wei(300_000),
            max_fee: Wei | None = None,
            max_priority_fee: Wei | None = None,
            tx_type: str | None = None
    ) -> TxParams:
        """
        Builds the transaction parameters.

        Args:
            value (TokenAmount): Transaction value.
            recipient (Optional[AnyAddress], optional): Recipient address. Defaults to None.
            raw_data (Optional[bytes | HexStr], optional): Raw data. Defaults to None.
            gas (Wei, optional): Gas limit. Defaults to 300,000.
            max_fee (Wei, optional): The maximum fee per gas. Defaults to None.
            max_priority_fee: (Wei, optional) The maximum priority fee per gas. Defaults to None.
            tx_type (str | None, optional): The transaction type. Defaults to None.

        Returns:
            TxParams: Transaction parameters.
        """
        pass

    @abstractmethod
    def transact(self, tx_params: TxParams, validate_status: bool = False) -> HexBytes:
        """
        Executes a transaction.

        Args:
            tx_params (TxParams): Transaction parameters.
            validate_status (bool, optional): Whether to validate the transaction status. Defaults to False.

        Returns:
            HexBytes: Transaction hash.
        """
        pass

    @abstractmethod
    def transfer(
            self,
            token: Token,
            recipient: AnyAddress,
            token_amount: TokenAmount,
            gas: Optional[Wei] = None,
            max_fee: Wei | None = None,
            max_priority_fee: Wei | None = None,
            validate_status: bool = False
    ) -> HexBytes:
        """
        Transfers tokens to a recipient.

        Args:
            token (Token): Token object.
            recipient (AnyAddress): Recipient address.
            token_amount (TokenAmount): Amount of tokens to transfer.
            gas (Optional[Wei], optional): Gas limit. Defaults to None.
            max_fee (Wei, optional): The maximum fee per gas. Defaults to None.
            max_priority_fee: (Wei, optional) The maximum priority fee per gas. Defaults to None.
            validate_status (bool, optional): Whether to validate the transaction status. Defaults to False.

        Returns:
            HexBytes: Transaction hash.
        """
        pass

    @abstractmethod
    def get_balance_of(self, token: Token, convert: bool = False) -> float:
        """
        Retrieves the balance of a specified token.

        Args:
            token (Token): Token object.
            convert (bool, optional): Whether to convert the balance from the smallest unit. Defaults to False.

        Returns:
            float: Token balance.
        """
        pass
