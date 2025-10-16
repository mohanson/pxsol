import pxsol.objectdict


develop = pxsol.objectdict.ObjectDict({
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

mainnet = pxsol.objectdict.ObjectDict({
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

testnet = pxsol.objectdict.ObjectDict({
    'commitment': 'confirmed',
    'log': 0,
    'rpc': {
        'qps': 1,
        'url': 'https://api.devnet.solana.com',
    },
    'spl': {}
})


current = develop
