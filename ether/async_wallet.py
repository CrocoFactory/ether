from __future__ import annotations

from typing import Optional
from eth_typing import HexStr
from hexbytes import HexBytes
from web3 import AsyncWeb3
from web3.contract.async_contract import AsyncContractFunction, AsyncContract
from web3.types import TxParams, Wei
from ether._base_wallet import _BaseWallet
from ether.types import Network, TokenAmount, AnyAddress, Token
from ether.utils import is_checksum_address


class AsyncWallet(_BaseWallet):
    """
    Async version of Wallet, interacting with your Ethereum digital wallet.
    You can change the network of the wallet at any time using the network setter.
    """

    def __init__(
            self,
            private_key: str,
            network: Network | str = 'Ethereum',
    ):
        """
        Args:
            private_key (str): Private key of the existing account.
            network (Network | str): Name of supported network or custom network information.
        """
        super().__init__(private_key, network, True)

    @property
    def provider(self) -> AsyncWeb3:
        """Gets the provider instance.

        Returns:
            AsyncWeb3: The asynchronous Web3 provider.
        """
        return self._provider

    def _load_token_contract(self, address: AnyAddress) -> AsyncContract:
        """Loads the token contract.

        Args:
            address (AnyAddress): The token contract address.

        Returns:
            AsyncContract: The token contract instance.
        """
        return super()._load_token_contract(address)

    async def get_balance(self, from_wei: bool = False) -> float | Wei:
        """Gets the balance of the current account in Ethereum or Wei units.

        Args:
            from_wei (bool, optional): Whether to convert the balance to Ether units. Defaults to False.

        Returns:
            float | Wei: The balance of the current account.
        """
        provider = self.provider
        balance = await provider.eth.get_balance(self.public_key)

        return balance if not from_wei else provider.from_wei(balance, 'ether')

    async def estimate_gas(self, tx_params: TxParams, from_wei: bool = False) -> Wei:
        """Estimates the gas required for a transaction.

        Args:
            tx_params (TxParams): The transaction parameters.
            from_wei (bool, optional): Whether to convert gas to Ether units. Defaults to False.

        Returns:
            Wei: The estimated gas in Wei units.
        """
        provider = self.provider
        gas = Wei(int(await provider.eth.estimate_gas(tx_params)))
        return gas if not from_wei else provider.from_wei(gas, 'ether')

    async def build_and_transact(
            self,
            closure: AsyncContractFunction,
            value: TokenAmount = 0,
            gas: Optional[int] = None,
            max_fee: Wei | None = None,
            max_priority_fee: Wei | None = None,
    ) -> HexBytes:
        """Builds and executes a transaction.

        Example:
            wallet = AsyncWallet(private_key)

            uniswap = provider.eth.contract(address=address, abi=abi)

            closure = uniswap.functions.swapExactETHForTokens(arg1, arg2, ...)

            await wallet.build_and_transact(closure, eth_amount)

        Args:
            closure (AsyncContractFunction): The contract function to call.
            value (TokenAmount, optional): Amount of network currency in Wei. Defaults to 0.
            gas (Optional[int], optional): Gas limit. Defaults to None.
            max_fee (Wei, optional): The maximum fee per gas. Defaults to None.
            max_priority_fee: (Wei, optional) The maximum priority fee per gas. Defaults to None.

        Returns:
            HexBytes: The transaction hash.
        """
        gas_ = Wei(300_000) if not gas else gas
        tx_params = await self.build_tx_params(value=value, gas=gas_, max_fee=max_fee, max_priority_fee=max_priority_fee)
        tx_params = await closure.build_transaction(tx_params)

        if not gas:
            gas = await self.estimate_gas(tx_params)
            tx_params['gas'] = gas

        return await self.transact(tx_params)

    async def approve(
            self,
            token: Token,
            contract_address: AnyAddress,
            token_amount: TokenAmount,
            gas: Optional[int] = None,
            max_fee: Wei | None = None,
            max_priority_fee: Wei | None = None,
    ) -> HexBytes:
        """Approves token usage for a specific contract.

        Args:
            token (Token): The token instance.
            contract_address (AnyAddress): The contract address.
            token_amount (TokenAmount): Amount of tokens to approve in Wei.
            gas (Optional[int], optional): Gas limit. Defaults to None.
            max_fee (Wei, optional): The maximum fee per gas. Defaults to None.
            max_priority_fee: (Wei, optional) The maximum priority fee per gas. Defaults to None.

        Returns:
            HexBytes: The transaction hash.

        Raises:
            ValueError: If the contract address is invalid.
        """
        if not is_checksum_address(contract_address):
            raise ValueError('Invalid contract address is provided')

        token = self._load_token_contract(token.address)
        contract_address = self.provider.to_checksum_address(contract_address)
        return await self.build_and_transact(
            token.functions.approve(contract_address, token_amount),
            gas=gas,
            max_fee=max_fee,
            max_priority_fee=max_priority_fee
        )

    async def build_tx_params(
            self,
            value: TokenAmount,
            recipient: Optional[AnyAddress] = None,
            raw_data: Optional[bytes | HexStr] = None,
            gas: Wei = Wei(100_000),
            max_fee: Wei | None = None,
            max_priority_fee: Wei | None = None,
            tx_type: str | None = None,
    ) -> TxParams:
        """Builds transaction parameters.

        Args:
            value (TokenAmount): The value in network currency to send in Wei.
            recipient (Optional[AnyAddress], optional): The recipient address. Defaults to None.
            raw_data (Optional[bytes | HexStr], optional): Transaction data. Defaults to None.
            gas (Wei, optional): The gas limit. Defaults to 300,000 Wei.
            max_fee (Wei, optional): The maximum fee per gas. Defaults to None.
            max_priority_fee: (Wei, optional) The maximum priority fee per gas. Defaults to None.
            tx_type (str | None, optional): The transaction type. Defaults to None.

        Returns:
            TxParams: The transaction parameters.
        """
        if not max_fee:
            latest_block = await self.provider.eth.get_block('latest')
            max_fee = latest_block['baseFeePerGas'] + 1000

        tx_params = {
            'from': self.public_key,
            'chainId': self.network.chain_id,
            'nonce': self.nonce,
            'value': value,
            'gas': gas,
            'maxFeePerGas': max_fee,
            'maxPriorityFeePerGas': max_priority_fee or max_fee * 0.1
        }

        if recipient:
            tx_params['to'] = self.provider.to_checksum_address(recipient)

        if raw_data:
            tx_params['data'] = raw_data

        if tx_type:
            tx_params['type'] = tx_type

        return tx_params

    async def transact(self, tx_params: TxParams) -> HexBytes:
        """Executes a transaction using the given parameters.

        Args:
            tx_params (TxParams): The transaction parameters.

        Returns:
            HexBytes: The transaction hash.
        """
        provider = self.provider
        signed_transaction = provider.eth.account.sign_transaction(tx_params, self.private_key)
        tx_hash = await provider.eth.send_raw_transaction(signed_transaction.rawTransaction)
        self._nonce += 1

        return tx_hash

    async def transfer(
            self,
            token: Token,
            recipient: AnyAddress,
            token_amount: TokenAmount,
            gas: Optional[Wei] = None,
            max_fee: Wei | None = None,
            max_priority_fee: Wei | None = None,
    ) -> HexBytes:
        """Transfers a token amount to another wallet.

        Args:
            token (Token): The token instance.
            recipient (AnyAddress): The recipient address.
            token_amount (TokenAmount): The amount of tokens to transfer in Wei.
            gas (Optional[Wei], optional): The gas limit. Defaults to None.
            max_fee (Wei, optional): The maximum fee per gas. Defaults to None.
            max_priority_fee: (Wei, optional) The maximum priority fee per gas. Defaults to None.

        Returns:
            HexBytes: The transaction hash.

        Raises:
            ValueError: If the recipient address is invalid.
        """
        if not is_checksum_address(recipient):
            raise ValueError('Invalid recipient address is provided')

        token_contract = self._load_token_contract(token.address)
        recipient = self.provider.to_checksum_address(recipient)
        closure = token_contract.functions.transfer(recipient, token_amount)
        return await self.build_and_transact(closure, Wei(0), gas, max_fee, max_priority_fee)

    async def get_balance_of(self, token: Token, convert: bool = False) -> float:
        """Gets the balance of a specified token.

        Args:
            token (Token): The token instance.
            convert (bool, optional): Whether to divide the balance by token decimals. Defaults to False.

        Returns:
            float: The token balance.
        """
        token_contract = self._load_token_contract(token.address)
        balance = await token_contract.functions.balanceOf(self.public_key).call()

        if convert:
            balance /= 10 ** token.decimals

        return balance

    async def get_token(self, address: AnyAddress) -> Token:
        """Retrieves token information from the specified address.

        Args:
            address (AnyAddress): The token contract address.

        Returns:
            Token: The token instance.

        Raises:
            ValueError: If the token address is invalid.
        """
        if not is_checksum_address(address):
            raise ValueError('Invalid token address is provided')

        address = self._provider.to_checksum_address(address)
        token_contract = self._load_token_contract(address)
        symbol = await token_contract.functions.symbol().call()
        decimals = await token_contract.functions.decimals().call()

        return Token(address=address, symbol=symbol, decimals=decimals)
