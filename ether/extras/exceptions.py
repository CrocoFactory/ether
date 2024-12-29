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


class InvalidRoute(ValueError):
    """Raised when provided token route is invalid"""
    def __init__(self, input_token: str, output_token: str, src_network: str, dest_network: str, defi: str):
        super().__init__(f"Token route {input_token} [{src_network}] --> {output_token} [{dest_network}] is "
                         f"not valid for {defi}")

        self.__input_token = input_token
        self.__output_token = output_token
        self.__src_network = src_network
        self.__dest_network = dest_network
        self.__defi = defi

    @property
    def input_token(self) -> str:
        return self.__input_token

    @property
    def output_token(self) -> str:
        return self.__output_token

    @property
    def src_network(self) -> str:
        return self.__src_network

    @property
    def dest_network(self) -> str:
        return self.__dest_network

    @property
    def defi(self) -> str:
        return self.__defi
