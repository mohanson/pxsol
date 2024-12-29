import pathlib
import pxsol


def test_program():
    user = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
    program_data = bytearray(pathlib.Path('res/hello_solana_program.so').read_bytes())
    program_pubkey = user.program_deploy(program_data)
    program_data_update = bytearray(pathlib.Path('res/hello_solana_program.so.2').read_bytes())
    user.program_update(program_pubkey, program_data_update)
    pxsol.rpc.step()
    user.program_closed(program_pubkey)


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


def test_spl():
    user = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
    hole = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(2))
    mint = user.spl_create(9)
    user.spl_create_account(mint)
    user.spl_mint(mint, 100 * 10**9)
    user.spl_transfer(mint, hole.pubkey, 1 * 10**9)
    assert hole.spl_balance(mint)[0] == 1 * 10**9
