import base64
import json
import pxsol.base58
import pxsol.config
import pxsol.core
import pxsol.denomination
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

    def program_buffer_closed(self, program_buffer_pubkey: pxsol.core.PubKey) -> None:
        # Close a buffer account. This method is used to withdraw all lamports when the buffer account is no longer in
        # use due to unexpected errors.
        rq = pxsol.core.Requisition(pxsol.core.ProgramLoaderUpgradeable.pubkey, [], bytearray)
        rq.account.append(pxsol.core.AccountMeta(program_buffer_pubkey, 1))
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 1))
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
        rq.data = pxsol.core.ProgramLoaderUpgradeable.close()
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [rq])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])

    def program_buffer_create(self, program: bytearray) -> pxsol.core.PubKey:
        # Writes a program into a buffer account. The buffer account is randomly generated, and its public key serves
        # as the function's return value.
        program_buffer_prikey = pxsol.core.PriKey(bytearray(random.randbytes(32)))
        program_buffer_pubkey = program_buffer_prikey.pubkey()
        program_data_size = pxsol.core.ProgramLoaderUpgradeable.size_program_data_metadata + len(program)
        # Sends a transaction which creates a buffer account large enough for the byte-code being deployed. It also
        # invokes the initialize buffer instruction to set the buffer authority to restrict writes to the deployer's
        # chosen address.
        r0 = pxsol.core.Requisition(pxsol.core.ProgramSystem.pubkey, [], bytearray())
        r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        r0.account.append(pxsol.core.AccountMeta(program_buffer_pubkey, 3))
        r0.data = pxsol.core.ProgramSystem.create_account(
            pxsol.rpc.get_minimum_balance_for_rent_exemption(program_data_size, {}),
            pxsol.core.ProgramLoaderUpgradeable.size_buffer_metadata + len(program),
            pxsol.core.ProgramLoaderUpgradeable.pubkey,
        )
        r1 = pxsol.core.Requisition(pxsol.core.ProgramLoaderUpgradeable.pubkey, [], bytearray())
        r1.account.append(pxsol.core.AccountMeta(program_buffer_pubkey, 1))
        r1.account.append(pxsol.core.AccountMeta(self.pubkey, 0))
        r1.data = pxsol.core.ProgramLoaderUpgradeable.initialize_buffer()
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [r0, r1])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey, program_buffer_prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])
        # Breaks up the program byte-code into ~1KB chunks and sends transactions to write each chunk with the write
        # buffer instruction.
        size = 1012
        hall = []
        for i in range(0, len(program), size):
            elem = program[i:i+size]
            rq = pxsol.core.Requisition(pxsol.core.ProgramLoaderUpgradeable.pubkey, [], bytearray())
            rq.account.append(pxsol.core.AccountMeta(program_buffer_pubkey, 1))
            rq.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
            rq.data = pxsol.core.ProgramLoaderUpgradeable.write(i, elem)
            tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [rq])
            tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
            tx.sign([self.prikey])
            assert len(tx.serialize()) <= 1232
            txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
            hall.append(txid)
        pxsol.rpc.wait(hall)
        return program_buffer_pubkey

    def program_closed(self, program_pubkey: pxsol.core.PubKey) -> None:
        # Close a program. The sol allocated to the on-chain program can be fully recovered by performing this action.
        program_data_pubkey = pxsol.core.ProgramLoaderUpgradeable.pubkey.derive(program_pubkey.p)
        rq = pxsol.core.Requisition(pxsol.core.ProgramLoaderUpgradeable.pubkey, [], bytearray())
        rq.account.append(pxsol.core.AccountMeta(program_data_pubkey, 1))
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 1))
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
        rq.account.append(pxsol.core.AccountMeta(program_pubkey, 1))
        rq.data = pxsol.core.ProgramLoaderUpgradeable.close()
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [rq])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])

    def program_deploy(self, program: bytearray) -> pxsol.core.PubKey:
        # Deploying a program on solana, returns the program's public key.
        program_buffer_pubkey = self.program_buffer_create(program)
        program_prikey = pxsol.core.PriKey(bytearray(random.randbytes(32)))
        program_pubkey = program_prikey.pubkey()
        program_data_pubkey = pxsol.core.ProgramLoaderUpgradeable.pubkey.derive(program_pubkey.p)
        # Deploy with max data len.
        r0 = pxsol.core.Requisition(pxsol.core.ProgramSystem.pubkey, [], bytearray())
        r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        r0.account.append(pxsol.core.AccountMeta(program_pubkey, 3))
        r0.data = pxsol.core.ProgramSystem.create_account(
            pxsol.rpc.get_minimum_balance_for_rent_exemption(pxsol.core.ProgramLoaderUpgradeable.size_program, {}),
            pxsol.core.ProgramLoaderUpgradeable.size_program,
            pxsol.core.ProgramLoaderUpgradeable.pubkey,
        )
        r1 = pxsol.core.Requisition(pxsol.core.ProgramLoaderUpgradeable.pubkey, [], bytearray())
        r1.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        r1.account.append(pxsol.core.AccountMeta(program_data_pubkey, 1))
        r1.account.append(pxsol.core.AccountMeta(program_pubkey, 1))
        r1.account.append(pxsol.core.AccountMeta(program_buffer_pubkey, 1))
        r1.account.append(pxsol.core.AccountMeta(pxsol.core.ProgramSysvarRent.pubkey, 0))
        r1.account.append(pxsol.core.AccountMeta(pxsol.core.ProgramSysvarClock.pubkey, 0))
        r1.account.append(pxsol.core.AccountMeta(pxsol.core.ProgramSystem.pubkey, 0))
        r1.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
        r1.data = pxsol.core.ProgramLoaderUpgradeable.deploy_with_max_data_len(len(program) * 2)
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [r0, r1])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey, program_prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])
        return program_pubkey

    def program_update(self, program: bytearray, program_pubkey: pxsol.core.PubKey) -> None:
        # Updating an existing solana program by new program data and the same program id.
        program_buffer_pubkey = self.program_buffer_create(program)
        program_data_pubkey = pxsol.core.ProgramLoaderUpgradeable.pubkey.derive(program_pubkey.p)
        rq = pxsol.core.Requisition(pxsol.core.ProgramLoaderUpgradeable.pubkey, [], bytearray())
        rq.account.append(pxsol.core.AccountMeta(program_data_pubkey, 1))
        rq.account.append(pxsol.core.AccountMeta(program_pubkey, 1))
        rq.account.append(pxsol.core.AccountMeta(program_buffer_pubkey, 1))
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 1))
        rq.account.append(pxsol.core.AccountMeta(pxsol.core.ProgramSysvarRent.pubkey, 0))
        rq.account.append(pxsol.core.AccountMeta(pxsol.core.ProgramSysvarClock.pubkey, 0))
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
        rq.data = pxsol.core.ProgramLoaderUpgradeable.upgrade()
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [rq])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])

    def sol_balance(self) -> int:
        # Returns the lamport balance of the account.
        return pxsol.rpc.get_balance(self.pubkey.base58(), {})

    def sol_transfer(self, pubkey: pxsol.core.PubKey, value: int) -> bytearray:
        # Transfers the specified lamports to the target. The function returns the first signature of the transaction,
        # which is used to identify the transaction (transaction id).
        rq = pxsol.core.Requisition(pxsol.core.ProgramSystem.pubkey, [], bytearray())
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        rq.account.append(pxsol.core.AccountMeta(pubkey, 1))
        rq.data = pxsol.core.ProgramSystem.transfer(value)
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [rq])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        assert pxsol.base58.decode(txid) == tx.signatures[0]
        pxsol.rpc.wait([txid])
        return tx.signatures[0]

    def sol_transfer_all(self, pubkey: pxsol.core.PubKey) -> bytearray:
        # Transfers all lamports to the target.
        # Solana's base fee is a fixed 5000 lamports (0.000005 SOL) per signature.
        return self.sol_transfer(pubkey, self.sol_balance() - 5000)

    def spl_addr(self, mint: pxsol.core.PubKey) -> pxsol.core.PubKey:
        seed = bytearray()
        seed.extend(self.pubkey.p)
        seed.extend(pxsol.core.ProgramToken.pubkey.p)
        seed.extend(mint.p)
        return pxsol.core.ProgramAssociatedTokenAccount.pubkey.derive(seed)

    def spl_balance(self, mint: pxsol.core.PubKey) -> typing.Dict[str, typing.Any]:
        r = pxsol.rpc.get_token_account_balance(self.spl_addr(mint).base58(), {})['value']
        r['amount'] = int(r['amount'])
        return r

    def spl_create(self) -> pxsol.core.PubKey:
        # Create a new token.
        mint_prikey = pxsol.core.PriKey(bytearray(random.randbytes(32)))
        mint_pubkey = mint_prikey.pubkey()
        r0 = pxsol.core.Requisition(pxsol.core.ProgramSystem.pubkey, [], bytearray())
        r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        r0.account.append(pxsol.core.AccountMeta(mint_pubkey, 3))
        r0.data = pxsol.core.ProgramSystem.create_account(
            pxsol.rpc.get_minimum_balance_for_rent_exemption(pxsol.core.ProgramToken.size_mint, {}),
            pxsol.core.ProgramToken.size_mint,
            pxsol.core.ProgramToken.pubkey,
        )
        r1 = pxsol.core.Requisition(pxsol.core.ProgramToken.pubkey, [], bytearray())
        r1.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
        r1.account.append(pxsol.core.AccountMeta(pxsol.core.ProgramSysvarRent.pubkey, 0))
        r1.data = pxsol.core.ProgramToken.initialize_mint(9, self.pubkey, self.pubkey)
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [r0, r1])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey, mint_prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])
        return mint_pubkey

    def spl_create_account(self, mint: pxsol.core.PubKey) -> pxsol.core.PubKey:
        account_pubkey = self.spl_addr(mint)
        rq = pxsol.core.Requisition(pxsol.core.ProgramAssociatedTokenAccount.pubkey, [], bytearray())
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        rq.account.append(pxsol.core.AccountMeta(account_pubkey, 1))
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 0))
        rq.account.append(pxsol.core.AccountMeta(mint, 0))
        rq.account.append(pxsol.core.AccountMeta(pxsol.core.ProgramSystem.pubkey, 0))
        rq.account.append(pxsol.core.AccountMeta(pxsol.core.ProgramToken.pubkey, 0))
        rq.data = pxsol.core.ProgramAssociatedTokenAccount.create()
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [rq])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])
        return account_pubkey

    def spl_mint(self, mint: pxsol.core.PubKey, amount: int) -> bytearray:
        account_pubkey = self.spl_addr(mint)
        rq = pxsol.core.Requisition(pxsol.core.ProgramToken.pubkey, [], bytearray())
        rq.account.append(pxsol.core.AccountMeta(mint, 1))
        rq.account.append(pxsol.core.AccountMeta(account_pubkey, 1))
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
        rq.data = pxsol.core.ProgramToken.mint_to(amount)
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [rq])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])
        return txid

    def spl_transfer(self, mint: pxsol.core.PubKey, pubkey: pxsol.core.PubKey, amount: int) -> bytearray:
        seed = bytearray()
        seed.extend(pubkey.p)
        seed.extend(pxsol.core.ProgramToken.pubkey.p)
        seed.extend(mint.p)
        hole_account_pubkey = pxsol.core.ProgramAssociatedTokenAccount.pubkey.derive(seed)
        r0 = pxsol.core.Requisition(pxsol.core.ProgramAssociatedTokenAccount.pubkey, [], bytearray())
        r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        r0.account.append(pxsol.core.AccountMeta(hole_account_pubkey, 1))
        r0.account.append(pxsol.core.AccountMeta(pubkey, 0))
        r0.account.append(pxsol.core.AccountMeta(mint, 0))
        r0.account.append(pxsol.core.AccountMeta(pxsol.core.ProgramSystem.pubkey, 0))
        r0.account.append(pxsol.core.AccountMeta(pxsol.core.ProgramToken.pubkey, 0))
        r0.data = pxsol.core.ProgramAssociatedTokenAccount.create_idempotent()
        r1 = pxsol.core.Requisition(pxsol.core.ProgramToken.pubkey, [], bytearray())
        r1.account.append(pxsol.core.AccountMeta(self.spl_addr(mint), 1))
        r1.account.append(pxsol.core.AccountMeta(mint, 0))
        r1.account.append(pxsol.core.AccountMeta(hole_account_pubkey, 1))
        r1.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
        r1.data = pxsol.core.ProgramToken.transfer_checked(amount, 9)
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [r0, r1])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])
        return txid
