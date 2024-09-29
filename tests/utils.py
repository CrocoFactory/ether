from functools import wraps


def validate_status(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        wallet = kwargs['wallet']
        tx_hash = await func(*args, **kwargs)
        status = bool(wallet.provider.eth.wait_for_transaction_receipt(tx_hash))

        assert status

    return wrapper
