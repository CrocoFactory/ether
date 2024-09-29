from typing import Any
from eth_utils import is_text, is_hex_address, to_checksum_address


def is_checksum_address(value: Any) -> bool:
    if not is_text(value):
        return False

    if not is_hex_address(value):
        return False

    is_equal = value.lower() == to_checksum_address(value).lower()
    return is_equal
