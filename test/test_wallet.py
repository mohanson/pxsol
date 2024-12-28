import pathlib
import pxsol


def test_program():
    user = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
    pubkey = user.program_deploy(bytearray(pathlib.Path('res/hello_solana_program.so').read_bytes()))
    user.program_update(bytearray(pathlib.Path('res/hello_solana_program.so.2').read_bytes()), pubkey)
    pxsol.rpc.step()
    user.program_closed(pubkey)


def test_program_buffer():
    user = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
    pubkey = user.program_buffer_create(bytearray(pathlib.Path('res/hello_solana_program.so').read_bytes()))
    pxsol.rpc.step()
    user.program_buffer_closed(pubkey)


def test_sol_transfer():
    user = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
    hole = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(2))
    a = hole.sol_balance()
    user.sol_transfer(hole.pubkey, 1 * pxsol.denomination.sol)
    b = hole.sol_balance()
    assert b == a + 1 * pxsol.denomination.sol


def test_sol_transfer_all():
    user = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
    hole = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(2))
    user.sol_transfer(hole.pubkey, 1 * pxsol.denomination.sol)
    hole.sol_transfer_all(user.pubkey)
    assert hole.sol_balance() == 0


def test_spl_addr():
    user = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
    addr = user.spl_addr(pxsol.core.PubKey.base58_decode('Dy97dJDN6N1hVJiUibC9LfQXkkDgk5h1TihP81Cs4vLK'))
    assert addr.base58() == '5JPFk5snZSg12D1PHpn5uUi1D6EWdBjMW2cjj5ZywMtm'


def test_spl():
    user = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
    spl_mint = user.spl_create()
    user.spl_create_account(spl_mint)
    user.spl_mint(spl_mint, 1 * 10**9)
