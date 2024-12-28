from __future__ import annotations

from typing import Optional
from eth_typing import HexStr
from hexbytes import HexBytes
from web3 import Web3
from web3.contract.contract import ContractFunction, Contract
from web3.types import TxParams, Wei, ABI
from ether._base_wallet import _BaseWallet
from ether.types import Network, TokenAmount, AnyAddress, Token
from ether.utils import is_checksum_address


class Wallet(_BaseWallet):
    """
    The class interacting with your Ethereum digital wallet.
    You can change the network of the wallet at any time using the network setter.
    """

    def __init__(
            self,
            private_key: str,
            network: Network | str = 'Ethereum',
    ):
        """
        Initializes a Wallet instance.

        Args:
            private_key (str): Private key of the existing account.
            network (Network | str): Name of the supported network or custom information about the network.
        """
        super().__init__(private_key, network, False)

    @property
    def provider(self) -> Web3:
        """Gets the Web3 provider instance.

        Returns:
            Web3: The Web3 provider.
        """
        return self._provider

    def _load_token_contract(self, address: AnyAddress, abi: ABI | None = None) -> Contract:
        """Loads the token contract for the given address.

        Args:
            address (AnyAddress): The token contract address.

        Returns:
            Contract: The token contract instance.
        """
        return super()._load_token_contract(address, abi)

    def get_balance(self, from_wei: bool = False) -> float | Wei:
        """Gets the balance of the current account in Ethereum or Wei units.

        Args:
            from_wei (bool, optional): Whether to convert balance to Ether units. Defaults to False.

        Returns:
            float | Wei: The balance of the current account.
        """
        provider = self.provider
        balance = provider.eth.get_balance(self.public_key)

        return balance if not from_wei else provider.from_wei(balance, 'ether')

    def estimate_gas(self, tx_params: TxParams, from_wei: bool = False) -> Wei:
        """Estimates the gas required for a transaction.

        Args:
            tx_params (TxParams): The transaction parameters.
            from_wei (bool, optional): Whether to convert gas to Ether units. Defaults to False.

        Returns:
            Wei: The estimated gas in Wei units.
        """
        provider = self.provider
        gas = Wei(int(provider.eth.estimate_gas(tx_params)))
        return gas if not from_wei else provider.from_wei(gas, 'ether')

    def build_and_transact(
            self,
            closure: ContractFunction,
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
        gas_ = Wei(300_000) if not gas else gas
        tx_params = self.build_tx_params(value=value, gas=gas_, max_fee=max_fee, max_priority_fee=max_priority_fee)
        tx_params = closure.build_transaction(tx_params)

        if not gas:
            gas = self.estimate_gas(tx_params)
            tx_params['gas'] = gas

        return self.transact(tx_params, validate_status=validate_status)

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
        if not is_checksum_address(contract_address):
            raise ValueError('Invalid contract address is provided')

        token = self._load_token_contract(token.address)
        contract_address = self.provider.to_checksum_address(contract_address)
        return self.build_and_transact(
            token.functions.approve(contract_address, token_amount),
            gas=gas,
            max_fee=max_fee,
            max_priority_fee=max_priority_fee,
            validate_status=validate_status
        )

    def build_tx_params(
            self,
            value: TokenAmount,
            recipient: Optional[AnyAddress] = None,
            raw_data: Optional[bytes | HexStr] = None,
            gas: Wei = Wei(300_000),
            max_fee: Wei | None = None,
            max_priority_fee: Wei | None = None,
            tx_type: str | None = None,
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
        if not max_fee:
            latest_block = self.provider.eth.get_block('latest')
            max_fee = latest_block['baseFeePerGas']

        tx_params = {
            'from': self.public_key,
            'chainId': self.network.chain_id,
            'nonce': self.nonce,
            'value': value,
            'gas': gas,
            'maxFeePerGas': max_fee,
            'maxPriorityFeePerGas': max_priority_fee or int(max_fee * 0.05)
        }

        if recipient:
            tx_params['to'] = self.provider.to_checksum_address(recipient)

        if raw_data:
            tx_params['data'] = raw_data

        if tx_type:
            tx_params['type'] = tx_type

        return tx_params

    def transact(self, tx_params: TxParams, validate_status: bool = False) -> HexBytes:
        """
        Executes a transaction.

        Args:
            tx_params (TxParams): Transaction parameters.
            validate_status: (bool): Whether to validate the transaction status. Defaults to False.

        Returns:
            HexBytes: Transaction hash.
        """
        provider = self.provider
        signed_transaction = provider.eth.account.sign_transaction(tx_params, self.private_key)
        tx_hash = provider.eth.send_raw_transaction(signed_transaction.rawTransaction)
        self._nonce += 1

        if validate_status:
            receipt = provider.eth.wait_for_transaction_receipt(tx_hash)
            if receipt.status != 1:
                raise ValueError(f"Transaction failed with status {receipt.status}. Receipt: {receipt}")

        return tx_hash

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
        if not is_checksum_address(recipient):
            raise ValueError('Invalid recipient address is provided')

        token_contract = self._load_token_contract(token.address)
        recipient = self.provider.to_checksum_address(recipient)
        closure = token_contract.functions.transfer(recipient, token_amount)
        return self.build_and_transact(closure, Wei(0), gas, max_fee, max_priority_fee, validate_status)

    def get_balance_of(self, token: Token, convert: bool = False) -> float:
        """Gets the balance of a specified token.

        Args:
            token (Token): The token instance.
            convert (bool, optional): Whether to convert the balance by dividing it by token decimals. Defaults to False.

        Returns:
            float: The token balance.
        """
        token_contract = self._load_token_contract(token.address)
        balance = token_contract.functions.balanceOf(self.public_key).call()

        if convert:
            balance /= 10 ** token.decimals

        return balance

    def get_token(self, address: AnyAddress, abi: ABI | None = None) -> Token:
        """Retrieves token information from the specified address.

        Args:
            address (AnyAddress): The token contract address.
            abi (ABI | None, optional): Contract ABI. Defaults to USDT ABI.

        Returns:
            Token: The token instance.

        Raises:
            ValueError: If the token address is invalid.
        """
        if not is_checksum_address(address):
            raise ValueError('Invalid token address is provided')

        address = self._provider.to_checksum_address(address)
        token_contract = self._load_token_contract(address, abi)
        symbol = token_contract.functions.symbol().call()
        decimals = token_contract.functions.decimals().call()

        return Token(address=address, symbol=symbol, decimals=decimals)
