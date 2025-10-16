import typing


class ObjectDict(dict):
    def __getattr__(self, name: str) -> typing.Any:
        try:
            value = self[name]
            if isinstance(value, dict):
                return ObjectDict(value)
            return value
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: typing.Any) -> None:
        self[name] = value


develop = ObjectDict({
    # The default state of a commitment, one of the confirmed or finalized.
    'commitment': 'confirmed',
    # Display log output.
    'log': 0,
    'rpc': {
        # Rate limit per second.
        'qps': 32,
        # Endpoint.
        'url': 'http://127.0.0.1:8899',
    },
    # Trusted spl token mint addresses.
    'spl': {}
})

mainnet = ObjectDict({
    'commitment': 'confirmed',
    'log': 0,
    'rpc': {
        'qps': 1,
        'url': 'https://api.mainnet-beta.solana.com',
    },
    'spl': {
        'pxs': '6B1ztFd9wSm3J5zD5vmMNEKg2r85M41wZMUW7wXwvEPH',
        'usdc': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
        'usdt': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',
    }
})

testnet = ObjectDict({
    'commitment': 'confirmed',
    'log': 0,
    'rpc': {
        'qps': 1,
        'url': 'https://api.devnet.solana.com',
    },
    'spl': {}
})


current = develop
