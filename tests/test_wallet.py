import pytest
from dotenv import dotenv_values

dotenv_values = dotenv_values()


@pytest.fixture
def wallet(make_wallet):
    return make_wallet(network='BSC', is_async=False, private_key=dotenv_values.get('TEST_PRIVATE_KEY'))


def test_get_balance(wallet):
    balance = wallet.get_balance()
    assert isinstance(balance, int)

    
def test_build_tx_params(wallet):
    tx_params = wallet.build_tx_params(0)
    assert 'value' in tx_params and 'gasPrice' in tx_params


def test_get_balance_of(wallet, usdc):
    assert isinstance(wallet.get_balance_of(usdc), int)
