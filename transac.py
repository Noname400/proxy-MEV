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


res = decode_tx('0x02f87005078459682f008459756b9e825208942a9beff4f79f7ed3bb0137cda50e3c65ac5102138609184e72a00080c080a068c1a5d87e9e15f14fe54741ce6621befdcfdf25661a5e687420e002481ff95ca037eb6140943a5edce6fedd12654bbce4701735929f1381caf802fc677bbf78c3')
print(res)