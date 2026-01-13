import base64
import json
import pxsol.base58
import pxsol.core
import pxsol.rpc
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

    def program_buffer(self, bincode: bytearray) -> pxsol.core.PubKey:
        # Writes a program into a buffer account. The buffer account is randomly generated, and its public key serves
        # as the function's return value.
        tempory_prikey = pxsol.core.PriKey.random()
        program_buffer = tempory_prikey.pubkey()
        pxsol.log.debugln(f'pxsol: program buffer prikey={tempory_prikey}')
        pxsol.log.debugln(f'pxsol: program buffer pubkey={program_buffer}')
        account_length = pxsol.program.LoaderUpgradeable.size_program_buffer + len(bincode)
        # Sends a transaction which creates a buffer account large enough for the byte-code being deployed. It also
        # invokes the initialize buffer instruction to set the buffer authority to restrict writes to the deployer's
        # chosen address.
        r0 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
        r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        r0.account.append(pxsol.core.AccountMeta(program_buffer, 3))
        r0.data = pxsol.program.System.create_account(
            pxsol.rpc.get_minimum_balance_for_rent_exemption(account_length, {}),
            account_length,
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
        program_data_pubkey = pxsol.program.LoaderUpgradeable.pubkey.derive_pda(program.p)[0]
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
        program_buffer = self.program_buffer(bincode)
        tempory_prikey = pxsol.core.PriKey.random()
        program = tempory_prikey.pubkey()
        program_data = pxsol.program.LoaderUpgradeable.pubkey.derive_pda(program.p)[0]
        pxsol.log.debugln(f'pxsol: program prikey={tempory_prikey}')
        pxsol.log.debugln(f'pxsol: program pubkey={program}')
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
        r1.data = pxsol.program.LoaderUpgradeable.deploy_with_max_data_len(len(bincode))
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [r0, r1])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey, tempory_prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])
        return program

    def program_update(self, program: pxsol.core.PubKey, bincode: bytearray) -> None:
        # Updating an existing solana program by new program data and the same program id.
        program_buffer = self.program_buffer(bincode)
        program_data = pxsol.program.LoaderUpgradeable.pubkey.derive_pda(program.p)[0]
        # Check the existing program data account size. If the new program data is larger than the existing one,
        # extend the program data account first.
        program_data_info = pxsol.rpc.get_account_info(program_data.base58(), {})
        assert len(base64.b64decode(program_data_info['data'][0])) == program_data_info['space']
        addi = pxsol.program.LoaderUpgradeable.size_program_data + len(bincode) - program_data_info['space']
        if addi > 0:
            pxsol.log.debugln(f'pxsol: extend program data addi={addi}')
            rq = pxsol.core.Requisition(pxsol.program.LoaderUpgradeable.pubkey, [], bytearray())
            rq.account.append(pxsol.core.AccountMeta(program_data, 1))
            rq.account.append(pxsol.core.AccountMeta(program, 1))
            rq.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
            rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
            rq.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
            rq.data = pxsol.program.LoaderUpgradeable.extend_program_checked(addi)
            tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [rq])
            tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
            tx.sign([self.prikey])
            txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
            pxsol.rpc.wait([txid])
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
        seed.extend(self.spl_host(mint).p)
        seed.extend(mint.p)
        return pxsol.program.AssociatedTokenAccount.pubkey.derive_pda(seed)[0]

    def spl_balance(self, mint: pxsol.core.PubKey) -> typing.List[int]:
        # Returns the current token balance and the decimals of the token.
        r = pxsol.rpc.get_token_account_balance(self.spl_account(mint).base58(), {})['value']
        return [int(r['amount']), r['decimals']]

    def spl_create(self, decimals: int, extension: typing.Dict[str, typing.Any]) -> pxsol.core.PubKey:
        # Create a new token mint with specified decimals and extension. Returns the mint public key.
        # Supported extensions:
        # * default_account_state: int
        # * metadata: { name: str, symbol: str, uri: str }
        mint_prikey = pxsol.core.PriKey.random()
        mint_pubkey = mint_prikey.pubkey()
        mint_size = pxsol.program.Token.size_mint
        if len(extension) != 0:
            mint_size = pxsol.program.Token.size_extensions_base
        if 'default_account_state' in extension:
            mint_size += pxsol.program.Token.size_extensions_default_account_state
        if 'metadata' in extension:
            mint_size += pxsol.program.Token.size_extensions_metadata_pointer
        mint_lamports = pxsol.rpc.get_minimum_balance_for_rent_exemption(mint_size, {})
        rs = []
        rq = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
        rq.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        rq.account.append(pxsol.core.AccountMeta(mint_pubkey, 3))
        rq.data = pxsol.program.System.create_account(mint_lamports, mint_size, pxsol.program.Token.pubkey)
        rs.append(rq)
        if 'default_account_state' in extension:
            rq = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
            rq.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
            rq.data = pxsol.program.TokenExtensionDefaultAccountState.initialize(extension['default_account_state'])
            rs.append(rq)
        if 'metadata' in extension:
            rq = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
            rq.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
            rq.data = pxsol.program.TokenExtensionMetadataPointer.initialize(self.pubkey, mint_pubkey)
            rs.append(rq)
        rq = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
        rq.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
        rq.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))
        rq.data = pxsol.program.Token.initialize_mint(decimals, self.pubkey, self.pubkey)
        rs.append(rq)
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, rs)
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey, mint_prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])
        if 'metadata' in extension:
            name = extension['metadata']['name']
            symbol = extension['metadata']['symbol']
            uri = extension['metadata']['uri']
            addi_size = pxsol.program.Token.size_extensions_metadata + len(name) + len(symbol) + len(uri)
            addi_lamports = pxsol.rpc.get_minimum_balance_for_rent_exemption(mint_size + addi_size, {}) - mint_lamports
            r0 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
            r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
            r0.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
            r0.data = pxsol.program.System.transfer(addi_lamports)
            r1 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
            r1.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
            r1.account.append(pxsol.core.AccountMeta(self.pubkey, 0))
            r1.account.append(pxsol.core.AccountMeta(mint_pubkey, 0))
            r1.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
            r1.data = pxsol.program.TokenExtensionMetadata.initialize(name, symbol, uri)
            tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [r0, r1])
            tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
            tx.sign([self.prikey])
            txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
            pxsol.rpc.wait([txid])
        return mint_pubkey

    def spl_host(self, mint: pxsol.core.PubKey) -> pxsol.core.PubKey:
        # Returns the token program public key based on the mint account owner.
        info = pxsol.rpc.get_account_info(mint.base58(), {})
        host = pxsol.core.PubKey.base58_decode(info['owner'])
        assert host in [pxsol.program.Token.pubkey_2020, pxsol.program.Token.pubkey_2022]
        return host

    def spl_mint(self, mint: pxsol.core.PubKey, recv: pxsol.core.PubKey, amount: int) -> None:
        # Mint a specified number of tokens and distribute them to self. Note that amount refers to the smallest unit
        # of count, For example, when the decimals of token is 2, you should use 100 to represent 1 token. If the
        # token account does not exist, it will be created automatically.
        recv_atakey = Wallet.view_only(recv).spl_account(mint)
        r0 = pxsol.core.Requisition(pxsol.program.AssociatedTokenAccount.pubkey, [], bytearray())
        r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        r0.account.append(pxsol.core.AccountMeta(recv_atakey, 1))
        r0.account.append(pxsol.core.AccountMeta(recv, 0))
        r0.account.append(pxsol.core.AccountMeta(mint, 0))
        r0.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
        r0.account.append(pxsol.core.AccountMeta(pxsol.program.Token.pubkey, 0))
        r0.data = pxsol.program.AssociatedTokenAccount.create_idempotent()
        r1 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
        r1.account.append(pxsol.core.AccountMeta(mint, 1))
        r1.account.append(pxsol.core.AccountMeta(recv_atakey, 1))
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
        self_atakey = self.spl_account(mint)
        recv_atakey = Wallet.view_only(recv).spl_account(mint)
        r0 = pxsol.core.Requisition(pxsol.program.AssociatedTokenAccount.pubkey, [], bytearray())
        r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
        r0.account.append(pxsol.core.AccountMeta(recv_atakey, 1))
        r0.account.append(pxsol.core.AccountMeta(recv, 0))
        r0.account.append(pxsol.core.AccountMeta(mint, 0))
        r0.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
        r0.account.append(pxsol.core.AccountMeta(self.spl_host(mint), 0))
        r0.data = pxsol.program.AssociatedTokenAccount.create_idempotent()
        r1 = pxsol.core.Requisition(self.spl_host(mint), [], bytearray())
        r1.account.append(pxsol.core.AccountMeta(self_atakey, 1))
        r1.account.append(pxsol.core.AccountMeta(recv_atakey, 1))
        r1.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
        r1.data = pxsol.program.Token.transfer(amount)
        tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [r0, r1])
        tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
        tx.sign([self.prikey])
        txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
        pxsol.rpc.wait([txid])

    def spl_transfer_all(self, mint: pxsol.core.PubKey, recv: pxsol.core.PubKey) -> None:
        # Transfers all tokens to the target.
        amount = self.spl_balance(mint)[0]
        self.spl_transfer(mint, recv, amount)

    @classmethod
    def view_only(cls, pubkey: pxsol.core.PubKey) -> Wallet:
        # View only wallet let you monitor a wallet's balance and activity but you can't send, swap, or sign
        # transactions.
        r = Wallet(pxsol.core.PriKey.int_decode(1))
        r.pubkey = pubkey
        return r
