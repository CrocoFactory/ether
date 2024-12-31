from typing import Optional, Union
from typing_extensions import Self

from eth_typing import HexStr
from hexbytes import HexBytes
from web3 import Web3
from web3.contract.contract import ContractFunction, Contract
from web3.types import TxParams, Wei, ABI
from ._base_wallet import _BaseWallet
from .types import Network, TokenAmount, AnyAddress, Token
from .utils import is_checksum_address


class Wallet(_BaseWallet):
    """
    The Wallet class provides an interface for interacting with an Ethereum digital wallet.

    This class supports functionalities such as balance retrieval, transaction construction,
    token approvals, and transfers. It leverages the `web3.py` library for Ethereum blockchain interactions.

    Args:
        private_key: Account's key required for making (signing) transactions.
        network:
            The name of the built-inEthereum-based network or custom network configuration

            **Example**
            === "Network instance"
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

            === "Network Name (supported)"
                ```python
                from ether import Wallet
                my_wallet = Wallet('0xPrivateKey', 'Arbitrum')
                ```

    Example:
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
    """

    def __init__(
            self,
            private_key: str,
            network: Union[Network, str] = 'Ethereum',
    ):
        super().__init__(private_key, network, False)

    @property
    def provider(self) -> Web3:
        """
        Gets the `Web3` instance. It's required for instantiating contract instances

        Returns:
            Web3: The `Web3` instance.

        Example:
            ```python
            provider = wallet.provider

            # Define the ABI (Application Binary Interface) of the smart contract and the contract address
            stargate_abi = [...]
            stargate_router = '0x8731d54E9D02c286767d56ac03e8037C07e01e98'  # Contract address (Stargate Router)

            # Create a contract instance using the ABI and contract address
            stargate = wallet.provider.eth.contract(address=stargate_router, abi=stargate_abi)
            ```
        """
        return self._provider

    def _load_token_contract(self, address: AnyAddress, abi: Optional[ABI] = None) -> Contract:
        return super()._load_token_contract(address, abi)

    @classmethod
    def create(cls, network: Union[Network, str] = 'Ethereum') -> "Wallet":
        """
        Creates a new ethereum account and associated Wallet instance.

        Args:
            network: The name of the built-in Ethereum-based network or custom network configuration

        Returns:
            Self: Instance of Wallet.
        """
        return cls.create(network)

    def get_balance(self, from_wei: bool = False) -> Union[float, Wei]:
        """
        Retrieves the balance of the wallet.

        Args:
            from_wei: Whether to return the balance in ethereum units instead of Wei.

        Returns:
            float | Wei: The balance in Wei or ethereum.

        Example:
            ```python
            balance = wallet.get_balance(from_wei=True)
            print(f"Wallet Balance: {balance} ETH")
            ```
        """
        provider = self.provider
        balance = provider.eth.get_balance(self.public_key)

        return balance if not from_wei else provider.from_wei(balance, 'ether')

    def estimate_gas(self, tx_params: TxParams, from_wei: bool = False) -> Wei:
        """
        Estimates the gas for the given transaction params

        Args:
            tx_params: The transaction parameters.
            from_wei: Whether to return the gas value in Ether units.

        Returns:
            Wei: The estimated gas cost.

        Example:
            ```python
            tx_params = wallet.build_tx_params(...)
            gas_estimated = wallet.estimate_gas(tx_params)
            print(f"Estimated Gas: {gas_estimated}")
            ```
        """
        provider = self.provider
        gas = Wei(int(provider.eth.estimate_gas(tx_params)))
        return gas if not from_wei else provider.from_wei(gas, 'ether')

    def build_and_transact(
            self,
            closure: ContractFunction,
            value: TokenAmount = 0,
            gas: Optional[int] = None,
            max_fee: Optional[Wei] = None,
            max_priority_fee: Optional[Wei] = None,
            validate_status: bool = False
    ) -> HexBytes:
        """
        Builds and sends a transaction. It's based on getting closure as an argument. Closure is a transaction's function,
        called with arguments. Notice that it has to be not built

        Args:
            closure: Contract function.
            value: Transaction value. Defaults to 0.
            gas: Gas limit. Defaults to None.
            max_fee: The maximum fee per gas. Defaults to None.
            max_priority_fee: The maximum priority fee per gas. Defaults to None.
            validate_status: Whether to throw the error if the transaction status is bad. Defaults to False.

        Example:
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
            max_fee: Optional[Wei] = None,
            max_priority_fee: Optional[Wei] = None,
            validate_status: bool = False
    ) -> HexBytes:
        """
        Approves a specified amount of tokens for a contract.

        Args:
            token: Token object.
            contract_address: Contract address.
            token_amount: Amount of tokens to approve.
            gas: Gas limit. Defaults to None. If not provided, the default is 300,000.
            max_fee: The maximum fee per gas. If not provided, the base fee from the latest block will be used.
            max_priority_fee: The maximum priority fee per gas. If not provided, it will default to 5% of the `max_fee`.
            validate_status: Whether to throw the error if the transaction status is bad. Defaults to False.

        Example:
            ```python
            # Contract address (e.g., a DeFi protocol)
            contract_address = '0xContractAddressHere'
            amount_to_approve = 1000 * 10 ** token.decimals

            # Approve the contract to spend tokens
            approval_tx_hash = wallet.approve(token, contract_address, amount_to_approve)

            print(f"Approval transaction sent! Hash: {approval_tx_hash.hex()}")
            ```

        Raises:
            ValueError: If the provided contract address is not valid.

        Returns:
            HexBytes: Transaction hash.
        """
        if not is_checksum_address(contract_address):
            raise ValueError(f'Invalid contract address is provided: {contract_address}')

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
            raw_data: Optional[Union[bytes, HexStr]] = None,
            gas: Wei = Wei(300_000),
            max_fee: Optional[Wei] = None,
            max_priority_fee: Optional[Wei] = None,
            tx_type: Optional[str] = None,
    ) -> TxParams:
        """
        Builds the transaction parameters for a blockchain transaction.

        This method constructs the parameters required to send a transaction on the Ethereum blockchain,
        including the transaction value, recipient, gas limit, and fee details. It can also include
        raw data or a custom transaction type. It's used in conjunction with the [`transact`][ether.Wallet.transact] method to make transaction.

        Args:
            value: The number of tokens to be sent in the transaction.
            recipient: The recipient's address for the transaction.
            raw_data: The raw data to be included in the transaction.
            gas: The gas limit for the transaction. Default is 300,000.
            max_fee: The maximum fee per gas unit. If not provided,
                the base fee from the latest block will be used.
            max_priority_fee: The maximum priority fee per gas unit.
                If not provided, it will default to 5% of the `max_fee`.
            tx_type: The type of the transaction.

        Returns:
            TxParams: A dictionary containing the constructed transaction parameters.

        Example:
            ```python
            from ether import Wallet
            from hexbytes import HexBytes

            wallet = Wallet('0xPrivateKey', 'Ethereum')

            value = 1 * 10 ** 18 # 1 token to send
            recipient = "0xRecipientAddress"
            raw_data = HexBytes("0xRawData")

            tx_params = wallet.build_tx_params(
                value=value,
                recipient=recipient,
                raw_data=raw_data,
                gas=Wei(500_000),
                max_fee=Wei(1000),
                max_priority_fee=Wei(50),
                tx_type="0x2"
            )

            print(tx_params)
            ```

            This will output the constructed transaction parameters, like:
            ```python
            {
                'from': '0xYourPublicKey',
                'chainId': 1,
                'nonce': 5,
                'value': 1e18,
                'gas': Wei(500_000),
                'maxFeePerGas': Wei(1000),
                'maxPriorityFeePerGas': Wei(50),
                'to': '0xRecipientAddress',
                'data': HexBytes("0xRawData"),
                'type': '0x2'
            }
            ```
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
        Sends a transaction. It's used in conjunction with the [`build_tx_params`][ether.Wallet.build_tx_params] method to
        build transaction params.

        Args:
            tx_params: Transaction parameters.
            validate_status: Whether to throw the error if the transaction status is bad. Defaults to False.

        Raises:
            ValueError: If the transaction is failed and validate_status is True

        Example:
            ```python
            from ether import Wallet

            # Create a wallet instance
            wallet = Wallet('0xPrivateKey', 'Ethereum')

            # Define recipient and amount
            recipient = '0xRecipientAddressHere'
            amount_in_wei = 10 ** 18 # 1 Ether (in Wei)

            # Build transaction params and send the transaction
            params = wallet.build_tx_params(amount_in_wei, recipient)
            tx_hash = wallet.transact(params)

            print(f"Transaction sent! Hash: {tx_hash.hex()}")
            ```

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
            max_fee: Optional[Wei] = None,
            max_priority_fee: Optional[Wei] = None,
            validate_status: bool = False
    ) -> HexBytes:
        """
        Transfers ERC-20 tokens to a recipient. Don't use it to transfer native tokens (like ETH in Ethereum, Arbitrum),
        instead use the `build_tx_params` and `transact` methods.

        Args:
            token: Token object.
            recipient: Recipient address.
            token_amount: Amount of tokens to transfer.
            gas: Gas limit. Defaults to None. If not provided, the default is 300,000.
            max_fee: The maximum fee per gas. If not provided, the base fee from the latest block will be used.
            max_priority_fee: The maximum priority fee per gas. If not provided, it will default to 5% of the `max_fee`.
            validate_status: Whether to throw the error if the transaction status is bad. Defaults to False.

        Raises:
            ValueError: If the recipient address is invalid.

        Example:
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

        Returns:
            HexBytes: Transaction hash.
        """
        if not is_checksum_address(recipient):
            raise ValueError(f'Invalid recipient address is provided: {recipient}')

        token_contract = self._load_token_contract(token.address)
        recipient = self.provider.to_checksum_address(recipient)
        closure = token_contract.functions.transfer(recipient, token_amount)
        return self.build_and_transact(closure, Wei(0), gas, max_fee, max_priority_fee, validate_status)

    def get_balance_of(self, token: Token, convert: bool = False) -> float:
        """
        Retrieves the balance of a specified token. Don't use it to get balance of native tokens (like ETH in Ethereum, Arbitrum),
        instead use the [`get_balance`][ether.AsyncWallet.get_balance] methods.

        Args:
            token: The token instance.
            convert: Whether to convert the balance using the token's decimals. Defaults to False.

        Returns:
            float: The balance of the token.

        Example:
            ```python
            # Get the token balance
            balance = wallet.get_balance_of(token, convert=True)
            print(f"Token Balance: {balance} {token.symbol}")
            ```
        """
        token_contract = self._load_token_contract(token.address)
        balance = token_contract.functions.balanceOf(self.public_key).call()

        if convert:
            balance /= 10 ** token.decimals

        return balance

    def get_token(self, address: AnyAddress, abi: Optional[ABI] = None) -> Token:
        """
        Retrieves the token information from the specified address and puts it to the Token instance

        Args:
            address: The token contract address.
            abi: Contract ABI. Defaults to USDT ABI.

        Returns:
            Token: The token instance.

        Example:
            ```python
            from ether import Wallet

            wallet = Wallet('0xPrivateKey', 'Ethereum')

            # Token details
            token_address = '0xTokenAddressHere'
            token = wallet.get_token(token_address)

            print(f"Token {token.symbol} is loaded!")
            ```

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
