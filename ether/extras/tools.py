from __future__ import annotations

import json
import re
from functools import wraps
from typing import Optional, Union
from eth_typing import ABI
from ether import Network, Wallet, AsyncWallet
from web3.contract import AsyncContract, Contract
from web3.main import BaseWeb3
from pathlib import Path
from .exceptions import ContractNotFound


def _snake_case(s: str) -> str:
    """
    Convert a string to the snake_case.

    Example:
        ```python
        print(snake_case('myParam'))
        ```

        ```text
        my_param
        ```

    Args:
          s (str): The string to convert.
    """
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    s = re.sub(r'\W+', '_', s).lower()
    s = re.sub(r'_+', '_', s)
    return s


ContractMap = dict[str, Union[AsyncContract, ABI, Contract]]


def load_contracts(
        provider: BaseWeb3,
        defi: str,
        network: Network | str,
        contracts_path: str | Path,
        version: Optional[int] = None
) -> ContractMap:
    folder_name = _snake_case(defi)
    path = Path(contracts_path) / Path(folder_name)

    if version:
        path /= Path(f'v{version}')

    contract_data = {}
    with open(path / Path("contracts.json")) as file:
        content = json.load(file)
        contract_names = content.keys()

        for name in contract_names:
            contract_content = content[name]
            if 'address' in contract_content:
                addresses = content[name]['address']
                if network not in addresses:
                    raise ContractNotFound(defi, network, addresses.keys())

                contract_data[name] = {'address': addresses[network]}

    for name in contract_names:
        with open(path / Path(f'{name}.abi')) as file:
            abi = json.load(file)
            if name in contract_data:
                contract_data[name]['abi'] = abi
            else:
                contract_data[f"{name}_abi"] = {'abi': abi}

    contracts = {}
    for key, value in contract_data.items():
        abi = value['abi']

        address = value.get('address')
        contracts[key] = provider.eth.contract(address=address, abi=abi) if address else abi

    return contracts


def change_network(contracts_path: Path | str):
    def decorator(func):
        """Decorator to reload contracts of DeFi before executing method if wallet instance changed the network."""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            network = self.network
            wallet: Wallet | AsyncWallet = self.wallet

            if network != wallet.network:
                defi = self._name or self.__class__.__name__

                try:
                    version = self.version
                except AttributeError:
                    version = None

                contracts = load_contracts(wallet.provider, defi, wallet.network.name, contracts_path, version)

                for key, value in contracts.items():
                    setattr(self, f'_{key}', value)

                self._network = wallet.network
                self._provider = wallet.provider

            return func(self, *args, **kwargs)

        return wrapper
    return decorator
