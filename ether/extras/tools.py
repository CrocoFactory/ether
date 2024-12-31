"""
Utility functions for working with smart contracts
"""

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
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    s = re.sub(r'\W+', '_', s).lower()
    s = re.sub(r'_+', '_', s)
    return s


ContractMap = dict[str, Union[AsyncContract, ABI, Contract]]


def load_contracts(
        provider: BaseWeb3,
        defi: str,
        network: Union[Network, str],
        contracts_path: Union[str, Path],
        version: Optional[int] = None
) -> ContractMap:
    """
    Load contract data from JSON and ABI files.

    Function requires that snake-cased defi name match with the corresponding folder containing data of contracts.

    Folder structure:

    ```text
    contracts/ <--- This path corresponds to contracts_path argument
    │
    ├── defi1/
    │   ├── contracts.json
    │   ├── contract1.abi
    │   └── contract2.abi
    │
    └── defi2/
        ├── contracts.json
        ├── contract1.abi
        └── contract2.abi
    ```

    If you want to support multiple versions of DeFi protocol, you must have the following folder structure. Sub-folder
    of DeFi folder must have the format `v[VERSION_NUMBER]`

    ```text
    contracts/  <--- This path corresponds to contracts_path argument
    │
    └── defi/
        ├── v1/
        │   ├── contracts.json
        │   ├── contract1.abi
        │   └── contract2.abi
        │
        └── v2/
            ├── contracts.json
            └── contract1.abi
    ```

    Structure of contracts.json:

    ```json
    {
      "contract1": {
        "abi": "contract1.abi",
        "address": {
          "Arbitrum": "0xe977Fa8D8AE7D3D6e28c17A868EF04bD301c583f",
          "Optimism": "0xe977Fa8D8AE7D3D6e28c17A868EF04bD301c583f"
        }
      },
      "contract2": {
        "abi": "contract2.abi",
        "address": {
          "Arbitrum": "0xe977Fa8D8AE7D3D6e28c17A868EF04bD301c583f",
          "Optimism": "0x2B4069517957735bE00ceE0fadAE88a26365528f",
        }
      }
    }
    ```

    Args:
        provider: An instance of AsyncWeb3 or Web3.
        defi: The name of the DeFi.
        network: The name of the built-in Ethereum-based network or custom network configuration
        contracts_path: The path to the directory containing subfolders with contracts.json and ABI files.
        version: Optional version number of the DeFi protocol. Specify when DeFi folder contains multiple subfolders
                    for specific versions of DeFi protocol.

    Example:
        ```python
        class _UniswapProxy:
            def __init__(
                    self,
                    wallet: AsyncWallet,
                    defi_name: DefiName,
                    router: AsyncContract,
                    factory: AsyncContract,
                    pool_abi: ABI,
                    quoter_v2: Optional[AsyncContract] = None,
                    non_fungible_position_manager: Optional[AsyncContract] = None,
                    version: ContractVersion = 2,
            ):
                self.__version = version

                match version:
                    case 2:
                        self.__proxy = UniswapRouterV2(
                            wallet,
                            defi_name,
                            router,
                            factory,
                            pool_abi
                        )
                    case 3:
                        self.__proxy = UniswapRouterV3(
                            wallet,
                            defi_name,
                            router,
                            factory,
                            quoter_v2,
                            non_fungible_position_manager,
                            pool_abi
                        )


        class Uniswap(_UniswapProxy):
            def __init__(
                    self,
                    wallet: AsyncWallet,
                    version: ContractVersion = 3
            ):
                contracts = load_contracts(
                    wallet.provider,
                    'Uniswap',
                    wallet.network.name,
                    CONTRACTS_PATH,
                    version
                )

                super().__init__(
                    wallet=wallet,
                    version=version,
                    defi_name='Uniswap',
                    **contracts
                )
        ```

    Returns:
           The dictionary mapping contract names to their corresponding contracts.
    """
    folder_name = _snake_case(defi)
    path = Path(contracts_path) / Path(folder_name)

    if isinstance(network, Network):
        network = network.name

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


def change_network(contracts_path: Union[Path, str]):
    """
    Decorator to reload contracts of DeFi before executing method if wallet instance changed the network.

    Args:
        contracts_path: The path to the directory containing subfolders with contracts.json and ABI files.

    Example:
        ```python
        from pathlib import Path

        CONTRACTS_PATH = Path(__file__).parent / Path('contracts')

        class Uniswap(Defi):
            def __init__(
                    self,
                    wallet: AsyncWallet,
            ):
                super().__init__(wallet=wallet, name='Uniswap', version=3)

            @change_network(CONTRACTS_PATH)
            async def swap(
                    self,
                    input_token: Token,
                    output_token: Token,
                    amount_in: TokenAmount,
                    slippage: float = 0.5,
                    from_wei: bool = True
            ) -> HexBytes:
                ...
        ```
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            network = self.network
            wallet: Union[Wallet, AsyncWallet] = self.wallet

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
