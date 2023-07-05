from eth.vm.forks.arrow_glacier.transactions import ArrowGlacierTransactionBuilder as TransactionBuilder
from eth_utils import (
  encode_hex,
  to_bytes,
)

def decode_tx(tx):
    original_hexstr = tx
    signed_tx_as_bytes = to_bytes(hexstr=original_hexstr)
    decoded_tx = TransactionBuilder().decode(signed_tx_as_bytes)
    sender = encode_hex(decoded_tx.sender)
    d = decoded_tx.__dict__
    return d['_inner'][5].hex(), d['_inner'][6], sender


res = decode_tx('0x02f87005058459682f008459690baf825208942a9beff4f79f7ed3bb0137cda50e3c65ac510213865af3107a400080c001a021c2b28315f4035cf841f109733802b3884d4f752cea241f32eaf029b3ffc068a05528cc8818909aa978b1fa0b9c4294e9c82f08de627af783e2fcdecefa7e0a35')
print(res)