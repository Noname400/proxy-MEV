from web3 import Web3
from eth.vm.forks.arrow_glacier.transactions import ArrowGlacierTransactionBuilder as TransactionBuilder
from eth_utils import (encode_hex,to_bytes,)

# Создайте экземпляр объекта Web3 и установите подключение к узлу Ethereum
w3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/4766aaf656954c52ae92eed6abc7f8cc'))

# Адрес отправителя транзакции
sender_address = '0x67146bDabd626dCCe75046148bae075b2d1006f5'

def decode_tx(tx):
    print(f'tx: {tx}')
    signed_tx_as_bytes = to_bytes(hexstr=tx)
    decoded_tx = TransactionBuilder().decode(signed_tx_as_bytes)
    print(f'decoded_tx: {decoded_tx}')
    sender = encode_hex(decoded_tx.sender)
    d = decoded_tx.__dict__
    print(f'D: {d}')
    return d['_inner'][5].hex(), d['_inner'][6], sender

try:
    # Получите актуальное значение nonce для отправителя
    nonce = w3.eth.get_transaction_count(sender_address)
    print(nonce)
    nonce_bytes = nonce.to_bytes(32, byteorder='big')
    # # Сырая транзакция в виде шестнадцатеричной строки
    raw_transaction = '0x02f870050d8459682f008459682f16825208942a9beff4f79f7ed3bb0137cda50e3c65ac510213865af3107a400080c080a0b255d653cfdb9325a53a820b02995c83734d58664fc7faafd62a8ed8ff53a31fa0088c8925ee91ae1cb00719ec2e706f82cad0209aa83667307e2e7b51904b739c'
    decode_tx(raw_transaction)
    # # Обновите nonce в сырой транзакции
    # updated_transaction = raw_transaction[:10] + hex(nonce)[2:].zfill(64) + raw_transaction[74:]
    updated_transaction = raw_transaction[:10] + nonce_bytes.hex() + raw_transaction[74:]

    print(updated_transaction)
    # # Отправка обновленной сырой транзакции
    tx_hash = w3.eth.send_raw_transaction(updated_transaction)
    print(f"Transaction sent. Hash: {tx_hash.hex()}")
except Exception as e:
    print(f"Failed to send transaction: {e}")
