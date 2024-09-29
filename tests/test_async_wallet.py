import pytest
from dotenv import dotenv_values

dotenv_values = dotenv_values()


@pytest.fixture()
def wallet(make_wallet):
    return make_wallet(network='BSC', is_async=True, private_key=dotenv_values.get('TEST_PRIVATE_KEY'))


@pytest.mark.asyncio
async def test_get_balance(wallet):
    balance = await wallet.get_balance()
    assert isinstance(balance, int)


@pytest.mark.asyncio
async def test_build_tx_params(wallet):
    tx_params = await wallet.build_tx_params(0)
    assert 'value' in tx_params and 'gasPrice' in tx_params


@pytest.mark.asyncio
async def test_get_balance_of(wallet, usdc):
    assert isinstance(await wallet.get_balance_of(usdc), int)


@pytest.mark.asyncio
async def test_transaction(wallet, eth_amount):
    recipient = '0xe977Fa8D8AE7D3D6e28c17A868EF04bD301c583f'
    params = await wallet.build_tx_params(eth_amount, recipient=recipient)
    return await wallet.transact(params)


@pytest.mark.asyncio
async def test_transfer(wallet, eth_amount, usdc):
    recipient = '0xe977Fa8D8AE7D3D6e28c17A868EF04bD301c583f'
    return await wallet.transfer(usdc, recipient, 10 ** (usdc.decimals - 2))
