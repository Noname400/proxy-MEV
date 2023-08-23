#!/usr/bin/python3
# encoding=utf-8
# -*- coding: utf-8 -*-
"""
@author: NonameHUNT
@GitHub: https://github.com/Noname400
@telegram: https://t.me/NonameHunt
"""
from signal import SIGINT, SIG_IGN, signal
from flask import Flask, request, render_template, redirect, url_for
from requests import get, post, exceptions
from json import dumps, loads
from time import time
from web3 import Web3
from os import path, mkdir
from datetime import datetime
from eth.vm.forks.arrow_glacier.transactions import ArrowGlacierTransactionBuilder as TransactionBuilder
from eth_utils import (encode_hex,to_bytes,)
import redis
import concurrent.futures
from multiprocessing import Pool
import sqlite3
from eth_account import Account, messages
from uuid import uuid4
from eth_account.account import Account, HexBytes
from eth_account.signers.local import LocalAccount
from lib.flashbots import flashbot
from web3 import Web3, HTTPProvider
from web3.exceptions import TransactionNotFound

version = 'proxy function bundle 1.16 / 20.08.23'
DB = 'database.db'
msg = ['already known', 'replacement transaction underpriced', 'ALREADY_EXISTS: already known', 'nonce too low', 'INTERNAL_ERROR: nonce too low']

def save_file(infile, text):
    if path.exists('log'): pass
    else: mkdir('log')
    file = f'log/{infile}.log'
    f = open(file, 'a', encoding='utf-8', errors='ignore')
    f.write(f'{text}\n')
    f.close()

try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    print("Successfully connected to Redis!")
except redis.ConnectionError as e:
    save_file('error-run-proxy', f"Error connecting to Redis: {str(e)}")
    print("Error connecting to Redis:", str(e))

scan_addr = ['0x7a250d5630b4cf539739df2c5dacb4c659f2488d','0xef1c6e67703c7bd7107eed8303fbe6ec2554bf6b','0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad', '0x4113B9c8F0d0357B99Ef2b86E3eb653e08449e6F', '0x01aE9431b618B60A29942EA108bF17fBb74b0eD8']

mainnet_providers = "https://api.speedynodes.net:8443/mainnet/eth-http?apikey=kCWonyiXqP9jbpzfozs6wckB6YspxqVg"
#"https://eth-mainnet.g.alchemy.com/v2/_iz-19CMM3I0UH2sI2viJ26bFOjd_Lis"

'''             #{"name": "beaverbuild", "url": "https://rpc.beaverbuild.org/", "method": "eth_sendRawTransaction"},
                #{"name": "rsync-builder", "url": "https://rsync-builder.xyz/", "method": "eth_sendPrivateRawTransaction"},
                #{"name": "builder0x69", "url": "http://builder0x69.io/", "method": "eth_sendRawTransaction"},
                #{"name": "titanbuilder1", "url": "https://rpc.titanbuilder.xyz/", "method": "eth_sendRawTransaction"},
                #{"name": "f1b.io", "url": "https://rpc.f1b.io/", "method": "eth_sendPrivateTransaction"},
'''
mev_providers = [
                {"name": "beaverbuild", "url": "https://rpc.beaverbuild.org/", "method": "eth_sendRawTransaction"},
                {"name": "rsync-builder", "url": "https://rsync-builder.xyz/", "method": "eth_sendPrivateRawTransaction"},
                {"name": "builder0x69", "url": "http://builder0x69.io/", "method": "eth_sendRawTransaction"},
                {"name": "titanbuilder1", "url": "https://rpc.titanbuilder.xyz/", "method": "eth_sendRawTransaction"},
                {"name": "f1b.io", "url": "https://rpc.f1b.io/", "method": "eth_sendPrivateTransaction"},
                {"name": "flashbots.net", "url": "https://relay.flashbots.net/", "method": "eth_sendPrivateTransaction"},
                {"name": "payload.de", "url": "https://rpc.payload.de/", "method": "eth_sendPrivateRawTransaction"},
                {"name": "lightspeedbuilder.info", "url": "https://rpc.lightspeedbuilder.info/", "method": "eth_sendPrivateRawTransaction"},
                {"name": "eth-builder", "url": "https://eth-builder.com/", "method": "eth_sendPrivateTransaction"}]

# mev_providers = [
#                 {"name": "flashbots", "url": "https://relay-goerli.flashbots.net", "method": "eth_sendPrivateRawTransaction"},
#                 {"name": "alchemy", "url": "https://eth-goerli.g.alchemy.com/v2/sN4cafcYL3h-XGF6seCLKyIZHm8qagr8", "method": "eth_sendRawTransaction"}]

#     ## TESTNET ###
# mainnet_providers = [
#     {"name": "test1", "url": "https://goerli.infura.io/v3/4766aaf656954c52ae92eed6abc7f8cc", "method": "eth_sendRawTransaction"},
#     {"name": "test2", "url": "https://goerli.blockpi.network/v1/rpc/public", "method": "eth_sendRawTransaction"},
#     {"name": "test3", "url": "https://eth-goerli.public.blastapi.io", "method": "eth_sendRawTransaction"},
#     {"name": "test4", "url": "https://goerli.gateway.tenderly.com", "method": "eth_sendRawTransaction"},
#     {"name": "test5", "url": "https://relay-goerli.flashbots.net", "method": "eth_sendPrivateRawTransaction"},
#     {"name": "test6", "url": "https://api.blocknative.com/v1/auction?network=goerli", "method": "eth_sendRawTransaction"},
#     {"name": "test7", "url": "https://goerli.edennetwork.io/v1/rpc", "method": "eth_sendRawTransaction"},
#     {"name": "alchemy", "url": "https://eth-goerli.g.alchemy.com/v2/sN4cafcYL3h-XGF6seCLKyIZHm8qagr8", "method": "eth_sendRawTransaction"}]

class data():
    def __init__(self):
        self.w3 = Web3()
        self.w3_providers = Web3(HTTPProvider('https://api.speedynodes.net:8443/mainnet/eth-http?apikey=kCWonyiXqP9jbpzfozs6wckB6YspxqVg'))
        self.mainnet_providers = "https://api.speedynodes.net:8443/mainnet/eth-http?apikey=kCWonyiXqP9jbpzfozs6wckB6YspxqVg"
        self.pvk = 0xa2bd3f0d8b52bea2c644bb5029dc868147bc29296ba63428124ce32807d0e207
        self.request = {}
        self.jsonrpc = ''
        self.id = 0
        self.method = ""
        self.result = ""
        self.params = []
        self.blockNumber = 0
        self.bundleHash_ = ""
        self.hash_tx_ = ""
        self.from_ = ""
        self.to_ = ""
        self.value_ = 0
        self.ip_ = ""
        self.headers = {"accept":"application/json", "content-type":"application/json"}
        self.num_threads_mev = len(mev_providers)
        self.num_threads_provider = len(mainnet_providers)

    def dict_redis(self):
        return {"ip": self.ip_, "from": self.from_, "to": self.to_, "value": self.value_, "url_provider": self.mainnet_providers}

    def dict_bundle(self):
        return {'jsonrpc': self.jsonrpc, 'id': self.id, 'result': {"bundleHash": self.bundleHash_}}

    def dict_hash_tx(self):
        return {'jsonrpc': self.jsonrpc, 'id': self.id, 'result': self.hash_tx_}

    def create_hash_tx(self):
        self.hash_tx_ = self.w3.keccak(hexstr=self.params[0][2:]).hex()
        
    def create_hash_tx_bundle(self):
        sum_h = ''
        for h in self.params[0]['txs']:
            sum_h = sum_h + self.w3.keccak(hexstr = h[2:]).hex()[2:]
        self.bundleHash_ = self.w3.keccak(hexstr = sum_h).hex()      

    def decode_tx_raw(self):
        signed_tx_as_bytes = to_bytes(hexstr=self.params[0][2:])
        decoded_tx = TransactionBuilder().decode(signed_tx_as_bytes)
        self.from_ = encode_hex(decoded_tx.sender)
        d = decoded_tx.__dict__
        self.to_ = f'0x{d["_inner"][5].hex()}'
        self.value_ = d['_inner'][6]
        save_file('raw',f'{d} | {decoded_tx}')

    def decode_tx_bundle(self):
        signed_tx_as_bytes = to_bytes(hexstr=self.params[0]['txs'][0][2:])
        decoded_tx = TransactionBuilder().decode(signed_tx_as_bytes)
        self.from_ = encode_hex(decoded_tx.sender)
        d = decoded_tx.__dict__
        self.to_ = f'0x{d["_inner"][5].hex()}'
        self.value_ = d['_inner'][6]

    def get_current_block_number(self):
        payload = {"id": 1, "jsonrpc": "2.0", "method": "eth_blockNumber"}
        response = post(self.fast_provider, json=payload, headers=self.headers)
        data = response.json()
        self.blockNumber = int(data["result"], 16)

def fill_class(data, data_dict):
    data.__dict__.update(data_dict)

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_worker():
    signal(SIGINT, SIG_IGN)

def create_db(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS allow_users (id INTEGER PRIMARY KEY, addr TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS stat (id INTEGER PRIMARY KEY, ip_ TEXT, from_ TEXT, to_ TEXT, value_ TEXT, count_ INTEGER, tip_ TEXT, timestamp_ TEXT)')
    conn.commit()
    conn.close()

def date_str():
    now = datetime.now()
    return now.strftime("%Y/%m/%d/, %H:%M:%S")

def search_allow(table, addr):
    connection = sqlite3.connect(DB)
    cursor = connection.cursor()
    cursor.execute(f'SELECT EXISTS (SELECT 1 FROM {table} WHERE addr = ?)', (addr,))
    result = cursor.fetchone()[0]
    connection.close()
    return bool(result)

def save_stat(ip_, from_, to_, value_, tip_):
    counts = 0
    conn = sqlite3.connect(DB)
    select_query = "SELECT count_ FROM stat WHERE from_ = ? AND to_ = ?"
    existing_row_from_to = conn.execute(select_query, (from_, to_)).fetchone()
    
    if existing_row_from_to is not None:
        counts = existing_row_from_to[0] + 1
        update_query = "UPDATE stat SET from_ = ?, to_ = ?, value_ = ?, count_ = ?, timestamp_ = ?  WHERE from_ = ? AND to_ = ?"
        conn.execute(update_query, (from_, to_, value_, counts, date_str(), from_, to_))
        conn.commit()
        conn.close()

    else:
        insert_query = "INSERT INTO stat (ip_, from_, to_, value_, count_, tip_, timestamp_) VALUES (?, ?, ?, ?, ?, ?, ?)"
        conn.execute(insert_query, (ip_, from_, to_, value_, 1, tip_, date_str()))
        conn.commit()
        conn.close()
    
def searsh_list(s:str, l:list):
    for e in l:
        if e.lower() == s.lower():
            return True
    return False

def send_bundle_proxy(url_mev, url_provider, raw, addr_to):
    signer: LocalAccount = Account.from_key(0xa2bd3f0d8b52bea2c644bb5029dc868147bc29296ba63428124ce32807d0e207)
    w3 = Web3(HTTPProvider(url_provider)) #'https://api.speedynodes.net:8443/mainnet/eth-http?apikey=kCWonyiXqP9jbpzfozs6wckB6YspxqVg'
    flashbot(w3, signer, url_mev) #'https://relay.flashbots.net'
    #tx1_signed2 = HexBytes('02f874018202418405f5e1008503dcf01e14825208944113b9c8f0d0357b99ef2b86e3eb653e08449e6f87038d7ea4c6800080c001a024c1b2016977fa3878e09e36c7107e086fc4511d1e333a5d2dcb663ae26c014ca0390edd72330aebfbd56cae480dcdf18e2953cc3e7fb80d4c78cca342e20911bc') #sender.sign_transaction(tx1)
    tx1_signed2 = HexBytes(raw)
    bundle = [
        {"signed_transaction": tx1_signed2},]
    while True:
        block = w3.eth.block_number
        print(f"Block {block}")
        #w3.flashbots.simulate(bundle, block)
        # try:
        #     w3.flashbots.simulate(bundle, block)
        #     print("Simulation successful.")
        # except Exception as e:
        #     print("Simulation error", e)
        #     return
        # finally:
        #print(f"Sending bundle targeting block {block + 1}")
        replacement_uuid = str(uuid4())
        print(f"replacementUuid {replacement_uuid}")
        send_result = w3.flashbots.send_bundle(bundle, target_block_number=block + 1, opts={"replacementUuid": replacement_uuid},)
        print("bundleHash", w3.toHex(send_result.bundle_hash()))

            # stats_v1 = w3.flashbots.get_bundle_stats(
            #     w3.toHex(send_result.bundle_hash()), block
            # )
            # print("bundleStats v1", stats_v1)

            # stats_v2 = w3.flashbots.get_bundle_stats_v2(
            #     w3.toHex(send_result.bundle_hash()), block
            # )
            # print("bundleStats v2", stats_v2)

        send_result.wait()
        try:
            receipts = send_result.receipts()
            print(f"\nBundle was mined in block {receipts[0].blockNumber}\a")
            break
        except TransactionNotFound:
            pass
            # print(f"Bundle not found in block {block+1}")
            # cancel_res = w3.flashbots.cancel_bundles(replacement_uuid)
            # print(f"canceled {cancel_res}")
            
        checksum_addr_to = Web3.to_checksum_address(addr_to)
        balance_wei = w3.eth.get_balance(checksum_addr_to)
        balance_eth = w3.fromWei(balance_wei, 'ether')

        print(f"Sender account balance: {balance_eth} ETH")
        # print(
        #     f"Receiver account balance: {Web3.fromWei(w3.eth.get_balance(receiverAddress), 'ether')} ETH"
        # )
        return True
