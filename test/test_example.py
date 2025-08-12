import subprocess


def call(c: str):
    return subprocess.run(c, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def test_addr():
    call('python example/addr.py --prikey 0x1')


def test_balance():
    call('python example/balance.py --net develop --addr 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt')


def test_base58():
    call('python example/base58.py --decode 3Bxs46DNLk1oRbZR')
    call('python example/base58.py --encode 020000002007150000000000')


def test_genesis():
    call('python example/genesis.py')


def test_history():
    call('python example/history.py --addr 6ArN9XvxNndXKoZEgHECiC8M4LftBQ9nVdfyrC5tsii6 --limit 1')


def test_idjson():
    call('python example/idjson.py --idjson res/id.json')


def test_program():
    r = call('python example/program.py --action deploy --prikey 0x1')
    program_pubkey = r.stdout.decode().splitlines()[-1].rstrip().split()[1]
    call(f'python example/program.py --prikey 0x1 --action call --addr {program_pubkey}')
    call(f'python example/program.py --prikey 0x1 --action update --addr {program_pubkey}')
    call(f'python example/program.py --prikey 0x1 --action call --addr {program_pubkey}')
    call(f'python example/program.py --prikey 0x1 --action closed --addr {program_pubkey}')


def test_spl():
    path = 'https://raw.githubusercontent.com/mohanson/pxsol/refs/heads/master/res/pxs.json'
    r = call(f'python example/spl.py --prikey 0x1 --action create --name PXSOL --symbol PXS --uri {path}')
    mint = r.stdout.decode().splitlines()[-1].rstrip()
    call(f'python example/spl.py --prikey 0x1 --token {mint} --action mint --amount 100')
    call(f'python example/spl.py --prikey 0x1 --token {mint} --action balance')
    addr = '8pM1DN3RiT8vbom5u1sNryaNT1nyL8CTTW3b5PwWXRBH'
    call(f'python example/spl.py --prikey 0x1 --token {mint} --action transfer --to {addr} --amount 20')


def test_transfer():
    call('python example/transfer.py --prikey 0x1 --to 8pM1DN3RiT8vbom5u1sNryaNT1nyL8CTTW3b5PwWXRBH --value 0.05')


def test_wif():
    call('python example/wif.py --prikey 0x1')
