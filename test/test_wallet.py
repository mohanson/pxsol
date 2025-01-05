import base64
import pathlib
import pxsol
import random


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
    mint_name = 'Ethereum'
    mint_symbol = 'ETH'
    mint_uri = 'https://ethereum.org'
    mint_decimals = random.randint(0, 9)
    mint_exponent = 10**mint_decimals
    mint = user.spl_create(mint_name, mint_symbol, mint_uri, mint_decimals)
    mint_result = pxsol.rpc.get_account_info(mint.base58(), {})
    mint_info = pxsol.core.TokenMint.serialize_decode(bytearray(base64.b64decode(mint_result['data'][0])))
    assert mint_info.extension_metadata().name == mint_name
    assert mint_info.extension_metadata().symbol == mint_symbol
    assert mint_info.extension_metadata().uri == mint_uri
    mint_lamports = mint_result['lamports']
    mint_size = mint_result['space']
    assert pxsol.rpc.get_minimum_balance_for_rent_exemption(mint_size, {}) == mint_lamports
    mint_name = 'Ethereum Classic'
    mint_symbol = 'ETC'
    mint_uri = 'https://ethereumclassic.org/'
    user.spl_update(mint, mint_name, mint_symbol, mint_uri)
    mint_result = pxsol.rpc.get_account_info(mint.base58(), {})
    mint_info = pxsol.core.TokenMint.serialize_decode(bytearray(base64.b64decode(mint_result['data'][0])))
    assert mint_info.extension_metadata().name == mint_name
    assert mint_info.extension_metadata().symbol == mint_symbol
    assert mint_info.extension_metadata().uri == mint_uri
    mint_lamports = mint_result['lamports']
    mint_size = mint_result['space']
    assert pxsol.rpc.get_minimum_balance_for_rent_exemption(mint_size, {}) == mint_lamports
    mint_name = 'Ethereum'
    mint_symbol = 'ETH'
    mint_uri = 'https://ethereum.org'
    user.spl_update(mint, mint_name, mint_symbol, mint_uri)
    mint_result = pxsol.rpc.get_account_info(mint.base58(), {})
    mint_info = pxsol.core.TokenMint.serialize_decode(bytearray(base64.b64decode(mint_result['data'][0])))
    assert mint_info.extension_metadata().name == mint_name
    assert mint_info.extension_metadata().symbol == mint_symbol
    assert mint_info.extension_metadata().uri == mint_uri
    mint_lamports = mint_result['lamports']
    mint_size = mint_result['space']
    assert pxsol.rpc.get_minimum_balance_for_rent_exemption(mint_size, {}) == mint_lamports
    user.spl_create_account(mint)
    user.spl_mint(mint, user.pubkey, 99 * mint_exponent)
    user.spl_transfer(mint, hole.pubkey, 20 * mint_exponent)
    assert user.spl_balance(mint)[0] == 79 * mint_exponent
    assert hole.spl_balance(mint)[0] == 20 * mint_exponent
    user.spl_mint(mint, hole.pubkey, 10 * mint_exponent)
    assert user.spl_balance(mint)[0] == 79 * mint_exponent
    assert hole.spl_balance(mint)[0] == 30 * mint_exponent
