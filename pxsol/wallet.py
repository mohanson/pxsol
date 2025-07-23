import base64
import json
import pxsol.base58
import pxsol.core
import pxsol.rpc
import random
import typing


class Wallet:
    # A built-in solana wallet that can be used to perform most on-chain operations.

    def __init__(self, prikey: pxsol.core.PriKey) -> None:
        self.prikey = prikey
        self.pubkey = prikey.pubkey()

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> typing.Dict:
        return {
            'prikey': self.prikey.base58(),
            'pubkey': self.pubkey.base58(),
        }

    def program_buffer_closed(self, program_buffer: pxsol.core.PubKey) -> None:
        # Close a buffer account. This method is used to withdraw all lamports when the buffer account is no longer in
        # use due to unexpected errors.
        rq = pxsol.core.Requisition(pxsol.program.LoaderUpgradeable.pubkey, [], bytearray)
        rq.account.append(pxsol.core.AccountMeta(program_buffer, 1))
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 1))
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
        rq.data = pxsol.program.LoaderUpgradeable.close()
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [rq])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])

    def program_buffer_create(self, bincode: bytearray) -> pxsol.core.PubKey:
        # Writes a program into a buffer account. The buffer account is randomly generated, and its public key serves
        # as the function's return value.
        tempory_prikey = pxsol.core.PriKey.random()
        program_buffer = tempory_prikey.pubkey()
        # Sends a transaction which creates a buffer account large enough for the byte-code being deployed. It also
        # invokes the initialize buffer instruction to set the buffer authority to restrict writes to the deployer's
        # chosen address.
        r0 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
        r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        r0.account.append(pxsol.core.AccountMeta(program_buffer, 3))
        r0.data = pxsol.program.System.create_account(
            pxsol.rpc.get_minimum_balance_for_rent_exemption(
                pxsol.program.LoaderUpgradeable.size_program_data + len(bincode),
                {},
            ),
            pxsol.program.LoaderUpgradeable.size_program_buffer + len(bincode),
            pxsol.program.LoaderUpgradeable.pubkey,
        )
        r1 = pxsol.core.Requisition(pxsol.program.LoaderUpgradeable.pubkey, [], bytearray())
        r1.account.append(pxsol.core.AccountMeta(program_buffer, 1))
        r1.account.append(pxsol.core.AccountMeta(self.pubkey, 0))
        r1.data = pxsol.program.LoaderUpgradeable.initialize_buffer()
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [r0, r1])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey, tempory_prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])
        # Breaks up the program byte-code into ~1KB chunks and sends transactions to write each chunk with the write
        # buffer instruction.
        size = 1012
        hall = []
        for i in range(0, len(bincode), size):
            elem = bincode[i:i+size]
            rq = pxsol.core.Requisition(pxsol.program.LoaderUpgradeable.pubkey, [], bytearray())
            rq.account.append(pxsol.core.AccountMeta(program_buffer, 1))
            rq.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
            rq.data = pxsol.program.LoaderUpgradeable.write(i, elem)
            tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [rq])
            tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
            tx.sign([self.prikey])
            assert len(tx.serialize()) <= 1232
            txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
            hall.append(txid)
        pxsol.rpc.wait(hall)
        return program_buffer

    def program_closed(self, program: pxsol.core.PubKey) -> None:
        # Close a program. The sol allocated to the on-chain program can be fully recovered by performing this action.
        program_data_pubkey = pxsol.program.LoaderUpgradeable.pubkey.derive_pda(program.p)
        rq = pxsol.core.Requisition(pxsol.program.LoaderUpgradeable.pubkey, [], bytearray())
        rq.account.append(pxsol.core.AccountMeta(program_data_pubkey, 1))
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 1))
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
        rq.account.append(pxsol.core.AccountMeta(program, 1))
        rq.data = pxsol.program.LoaderUpgradeable.close()
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [rq])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])

    def program_deploy(self, bincode: bytearray) -> pxsol.core.PubKey:
        # Deploying a program on solana, returns the program's public key.
        tempory_prikey = pxsol.core.PriKey.random()
        program_buffer = self.program_buffer_create(bincode)
        program = tempory_prikey.pubkey()
        program_data = pxsol.program.LoaderUpgradeable.pubkey.derive_pda(program.p)
        # Deploy with max data len.
        r0 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
        r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        r0.account.append(pxsol.core.AccountMeta(program, 3))
        r0.data = pxsol.program.System.create_account(
            pxsol.rpc.get_minimum_balance_for_rent_exemption(pxsol.program.LoaderUpgradeable.size_program, {}),
            pxsol.program.LoaderUpgradeable.size_program,
            pxsol.program.LoaderUpgradeable.pubkey,
        )
        r1 = pxsol.core.Requisition(pxsol.program.LoaderUpgradeable.pubkey, [], bytearray())
        r1.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        r1.account.append(pxsol.core.AccountMeta(program_data, 1))
        r1.account.append(pxsol.core.AccountMeta(program, 1))
        r1.account.append(pxsol.core.AccountMeta(program_buffer, 1))
        r1.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))
        r1.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarClock.pubkey, 0))
        r1.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
        r1.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
        r1.data = pxsol.program.LoaderUpgradeable.deploy_with_max_data_len(len(bincode) * 2)
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [r0, r1])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey, tempory_prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])
        pxsol.rpc.step()
        return program

    def program_update(self, program: pxsol.core.PubKey, bincode: bytearray) -> None:
        # Updating an existing solana program by new program data and the same program id.
        program_buffer = self.program_buffer_create(bincode)
        program_data = pxsol.program.LoaderUpgradeable.pubkey.derive_pda(program.p)
        rq = pxsol.core.Requisition(pxsol.program.LoaderUpgradeable.pubkey, [], bytearray())
        rq.account.append(pxsol.core.AccountMeta(program_data, 1))
        rq.account.append(pxsol.core.AccountMeta(program, 1))
        rq.account.append(pxsol.core.AccountMeta(program_buffer, 1))
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 1))
        rq.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))
        rq.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarClock.pubkey, 0))
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
        rq.data = pxsol.program.LoaderUpgradeable.upgrade()
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [rq])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])
        pxsol.rpc.step()

    def sol_balance(self) -> int:
        # Returns the lamport balance of the account.
        return pxsol.rpc.get_balance(self.pubkey.base58(), {})

    def sol_transfer(self, recv: pxsol.core.PubKey, amount: int) -> None:
        # Transfers the specified lamports to the target. The function returns the first signature of the transaction,
        # which is used to identify the transaction (transaction id).
        rq = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        rq.account.append(pxsol.core.AccountMeta(recv, 1))
        rq.data = pxsol.program.System.transfer(amount)
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [rq])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        assert pxsol.base58.decode(txid) == tx.signatures[0]
        pxsol.rpc.wait([txid])

    def sol_transfer_all(self, recv: pxsol.core.PubKey) -> None:
        # Transfers all lamports to the target.
        # Solana's base fee is a fixed 5000 lamports (0.000005 SOL) per signature.
        self.sol_transfer(recv, self.sol_balance() - 5000)

    def spl_account(self, mint: pxsol.core.PubKey) -> pxsol.core.PubKey:
        # Returns associated token account.
        # See: https://solana.com/docs/core/tokens#associated-token-account.
        seed = bytearray()
        seed.extend(self.pubkey.p)
        info = pxsol.rpc.get_account_info(mint.base58(), {})
        host = pxsol.core.PubKey.base58_decode(info['owner'])
        assert host in [pxsol.program.Token.pubkey_2020, pxsol.program.Token.pubkey_2022]
        seed.extend(host.p)
        seed.extend(mint.p)
        return pxsol.program.AssociatedTokenAccount.pubkey.derive_pda(seed)

    def spl_balance(self, mint: pxsol.core.PubKey) -> typing.List[int]:
        # Returns the current token balance and the decimals of the token.
        r = pxsol.rpc.get_token_account_balance(self.spl_account(mint).base58(), {})['value']
        return [int(r['amount']), r['decimals']]

    def spl_create(self, name: str, symbol: str, uri: str, decimals: int) -> pxsol.core.PubKey:
        # Create a new token.
        mint_prikey = pxsol.core.PriKey.random()
        mint_pubkey = mint_prikey.pubkey()
        mint_size = pxsol.program.Token.size_extensions_base + pxsol.program.Token.size_extensions_metadata_pointer
        # Helper function to tack on the size of an extension bytes if an account with extensions is exactly the size
        # of a multisig.
        assert mint_size != 355
        addi_size = pxsol.program.Token.size_extensions_metadata + len(name) + len(symbol) + len(uri)
        mint_lamports = pxsol.rpc.get_minimum_balance_for_rent_exemption(mint_size + addi_size, {})
        r0 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
        r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        r0.account.append(pxsol.core.AccountMeta(mint_pubkey, 3))
        r0.data = pxsol.program.System.create_account(mint_lamports, mint_size, pxsol.program.Token.pubkey)
        r1 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
        r1.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
        r1.data = pxsol.program.Token.metadata_pointer_extension_initialize(self.pubkey, mint_pubkey)
        r2 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
        r2.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
        r2.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))
        r2.data = pxsol.program.Token.initialize_mint(decimals, self.pubkey, self.pubkey)
        r3 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
        r3.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
        r3.account.append(pxsol.core.AccountMeta(self.pubkey, 0))
        r3.account.append(pxsol.core.AccountMeta(mint_pubkey, 0))
        r3.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
        r3.data = pxsol.program.Token.metadata_initialize(name, symbol, uri)
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [r0, r1, r2, r3])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey, mint_prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])
        return mint_pubkey

    def spl_create_account(self, mint: pxsol.core.PubKey) -> pxsol.core.PubKey:
        # Create a token account. To track the individual ownership of each unit of a specific token, another type of
        # data account owned by the token program must be created.
        self_ata_pubkey = self.spl_account(mint)
        rq = pxsol.core.Requisition(pxsol.program.AssociatedTokenAccount.pubkey, [], bytearray())
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        rq.account.append(pxsol.core.AccountMeta(self_ata_pubkey, 1))
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 0))
        rq.account.append(pxsol.core.AccountMeta(mint, 0))
        rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
        rq.account.append(pxsol.core.AccountMeta(pxsol.program.Token.pubkey, 0))
        rq.data = pxsol.program.AssociatedTokenAccount.create()
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [rq])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])
        return self_ata_pubkey

    def spl_mint(self, mint: pxsol.core.PubKey, recv: pxsol.core.PubKey, amount: int) -> None:
        # Mint a specified number of tokens and distribute them to self. Note that amount refers to the smallest unit
        # of count, For example, when the decimals of token is 2, you should use 100 to represent 1 token. If the
        # token account does not exist, it will be created automatically.
        recv_ata_pubkey = Wallet.view_only(recv).spl_account(mint)
        r0 = pxsol.core.Requisition(pxsol.program.AssociatedTokenAccount.pubkey, [], bytearray())
        r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        r0.account.append(pxsol.core.AccountMeta(recv_ata_pubkey, 1))
        r0.account.append(pxsol.core.AccountMeta(recv, 0))
        r0.account.append(pxsol.core.AccountMeta(mint, 0))
        r0.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
        r0.account.append(pxsol.core.AccountMeta(pxsol.program.Token.pubkey, 0))
        r0.data = pxsol.program.AssociatedTokenAccount.create_idempotent()
        r1 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
        r1.account.append(pxsol.core.AccountMeta(mint, 1))
        r1.account.append(pxsol.core.AccountMeta(recv_ata_pubkey, 1))
        r1.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
        r1.data = pxsol.program.Token.mint_to(amount)
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [r0, r1])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])

    def spl_transfer(self, mint: pxsol.core.PubKey, recv: pxsol.core.PubKey, amount: int) -> None:
        # Transfers tokens to the target. Note that amount refers to the smallest unit of count, For example, when the
        # decimals of token is 2, you should use 100 to represent 1 token. If the token account does not exist, it will
        # be created automatically.
        self_ata_pubkey = self.spl_account(mint)
        recv_ata_pubkey = Wallet.view_only(recv).spl_account(mint)
        r0 = pxsol.core.Requisition(pxsol.program.AssociatedTokenAccount.pubkey, [], bytearray())
        r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        r0.account.append(pxsol.core.AccountMeta(recv_ata_pubkey, 1))
        r0.account.append(pxsol.core.AccountMeta(recv, 0))
        r0.account.append(pxsol.core.AccountMeta(mint, 0))
        r0.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
        r0.account.append(pxsol.core.AccountMeta(pxsol.program.Token.pubkey, 0))
        r0.data = pxsol.program.AssociatedTokenAccount.create_idempotent()
        r1 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
        r1.account.append(pxsol.core.AccountMeta(self_ata_pubkey, 1))
        r1.account.append(pxsol.core.AccountMeta(recv_ata_pubkey, 1))
        r1.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
        r1.data = pxsol.program.Token.transfer(amount)
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [r0, r1])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])

    def spl_update(self, mint: pxsol.core.PubKey, name: str, symbol: str, uri: str) -> None:
        # Update the token name, symbol and uri.
        mint_result = pxsol.rpc.get_account_info(mint.base58(), {})
        mint_size = mint_result['space']
        mint_lamports = mint_result['lamports']
        mint_info = pxsol.core.TokenMint.serialize_decode(bytearray(base64.b64decode(mint_result['data'][0])))
        mint_meta = mint_info.extension_metadata()
        mint_size -= len(mint_meta.name)
        mint_size -= len(mint_meta.symbol)
        mint_size -= len(mint_meta.uri)
        mint_size += len(name)
        mint_size += len(symbol)
        mint_size += len(uri)
        rent_lamports = pxsol.rpc.get_minimum_balance_for_rent_exemption(mint_size, {})
        r0 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
        r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        r0.account.append(pxsol.core.AccountMeta(mint, 1))
        r0.data = pxsol.program.System.transfer(rent_lamports - mint_lamports if rent_lamports > mint_lamports else 0)
        r1 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
        r1.account.append(pxsol.core.AccountMeta(mint, 1))
        r1.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
        r1.data = pxsol.program.Token.metadata_update_field('name', name)
        r2 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
        r2.account.append(pxsol.core.AccountMeta(mint, 1))
        r2.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
        r2.data = pxsol.program.Token.metadata_update_field('symbol', symbol)
        r3 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
        r3.account.append(pxsol.core.AccountMeta(mint, 1))
        r3.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
        r3.data = pxsol.program.Token.metadata_update_field('uri', uri)
        r4 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
        r4.account.append(pxsol.core.AccountMeta(mint, 1))
        r4.account.append(pxsol.core.AccountMeta(self.pubkey, 1))
        r4.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
        r4.data = pxsol.program.Token.withdraw_excess_lamports()
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [r0, r1, r2, r3, r4])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])

    @classmethod
    def view_only(cls, pubkey: pxsol.core.PubKey) -> typing.Self:
        # View only wallet let you monitor a wallet's balance and activity but you can't send, swap, or sign
        # transactions.
        r = cls(pxsol.core.PriKey.int_decode(1))
        r.pubkey = pubkey
        return r
