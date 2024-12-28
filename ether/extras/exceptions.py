from typing import Union


class ContractNotFound(OSError):
    """Raised when contract is not found in a specific network"""

    def __init__(self, defi: str, dest_network: str, supported_networks: list[str]):
        super().__init__(f"Contract is not found in {dest_network}. {defi} supports the following networks: "
                         f"{', '.join(supported_networks)}")
        self.__defi = defi
        self.__supported_networks = supported_networks
        self.__dest_network = dest_network

    @property
    def defi(self) -> str:
        return self.__defi

    @property
    def dest_network(self) -> str:
        return self.__dest_network

    @property
    def supported_networks(self) -> Union[list[str], tuple[str]]:
        return self.__supported_networks
