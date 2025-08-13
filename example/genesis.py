import pxsol

# Shows the accounts in the mainnet genesis block and their sol allocations.

PubKey = pxsol.bincode.Malloc(pxsol.bincode.U8, 32)
# List is unhashable type, so cannot be used as a dictionary key.
PubKey.decode = lambda x: pxsol.core.PubKey(bytearray(pxsol.bincode.Malloc(pxsol.bincode.U8, 32).decode(x)))

Account = pxsol.bincode.Struct([
    pxsol.bincode.U64,                       # Lamports
    pxsol.bincode.Vector(pxsol.bincode.U8),  # Data
    PubKey,                                  # Host
    pxsol.bincode.Bool,                      # Executable
    pxsol.bincode.U64,                       # Rent epoch
])

# See: https://github.com/anza-xyz/solana-sdk/blob/master/genesis-config/src/lib.rs
Genesis = pxsol.bincode.Struct([
    pxsol.bincode.I64,                                                                # Creation time
    pxsol.bincode.Dict([PubKey, Account]),                                            # Accounts
    pxsol.bincode.Vector(pxsol.bincode.Struct([pxsol.bincode.String, PubKey])),       # Native instruction processors
    pxsol.bincode.Dict([PubKey, Account]),                                            # Rewards pools
    pxsol.bincode.U64,                                                                # Ticks per slot
    pxsol.bincode.U64,                                                                # Unused
    pxsol.bincode.Struct([                                                            # Poh config
        pxsol.bincode.Struct([pxsol.bincode.U64, pxsol.bincode.U32]),
        pxsol.bincode.Option(pxsol.bincode.U64),
        pxsol.bincode.Option(pxsol.bincode.U64),
    ]),
    pxsol.bincode.U64,                                                                # Backwards compat with v0.23
    pxsol.bincode.Struct([                                                            # Fee rate governor
        pxsol.bincode.U64,
        pxsol.bincode.U64,
        pxsol.bincode.U64,
        pxsol.bincode.U64,
        pxsol.bincode.U64,
        pxsol.bincode.U8,
    ]),
    pxsol.bincode.Struct([pxsol.bincode.U64, pxsol.bincode.F64, pxsol.bincode.U8]),   # Rent
    pxsol.bincode.Struct([                                                            # Inflation
        pxsol.bincode.F64,
        pxsol.bincode.F64,
        pxsol.bincode.F64,
        pxsol.bincode.F64,
        pxsol.bincode.F64,
        pxsol.bincode.F64,
    ]),
    pxsol.bincode.Struct([                                                            # Epoch schedule
        pxsol.bincode.U64,
        pxsol.bincode.U64,
        pxsol.bincode.Bool,
        pxsol.bincode.U64,
        pxsol.bincode.U64,
    ]),
    pxsol.bincode.Enum,                                                                # Cluster type
])


with open('res/genesis.bin', 'rb') as f:
    conf = Genesis.decode(f)

accs = list(conf[1].items())
accs.sort(key=lambda x: -x[1][0])
for elem in accs:
    col0 = f'{elem[0].base58():<44}'
    col1 = f'{elem[1][0] / pxsol.denomination.sol:>12.2f}'
    print(col0, col1)
