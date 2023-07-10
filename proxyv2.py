#!/usr/bin/python3
# encoding=utf-8
# -*- coding: utf-8 -*-
"""
@author: NonameHUNT
@GitHub: https://github.com/Noname400
@telegram: https://t.me/NonameHunt
"""

from multiprocessing import Pool, freeze_support, cpu_count
from signal import SIGINT, SIG_IGN, signal
from flask import Flask, request, render_template
import requests
from requests import get, post
from json import dumps
from time import time
from web3 import Web3
from os import path, mkdir
from datetime import datetime
from eth.vm.forks.arrow_glacier.transactions import ArrowGlacierTransactionBuilder as TransactionBuilder
from eth_utils import (encode_hex,to_bytes,)
from sys import argv
import psutil
from hexbytes import HexBytes

version = 'proxy server 0.14 mainnet / 10.07.23'

app = Flask(__name__)

fast_mainnet_provider = ""
fast_mev_provider = ""
mev_addr = ['0x7a250d5630b4cf539739df2c5dacb4c659f2488d','0xef1c6e67703c7bd7107eed8303fbe6ec2554bf6b','0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad']


stat_server = '127.0.0.1:3200'
headers = {'Content-Type': 'application/json'}
telegram_token = '5311024399:AAF6Ov-sMSc4dd2DDdx0hF_B-5-4vPerFTs'
telegram_channel_id = '@scanpvknon'

mainnet_providers = [
    {
        "name": "Infura",
        "url": "https://mainnet.infura.io/v3/4766aaf656954c52ae92eed6abc7f8cc"
    },
    {
        "name": "QuickNode",
        "url": "https://frequent-flashy-theorem.discover.quiknode.pro/7e58b0a32c49c77019714bded2cb0d88420fb393/"
    },
    {
        "name": "Alchemy",
        "url": "https://eth-mainnet.g.alchemy.com/v2/gBGU0r8-WxEIo4gyN5Qrdu47hahJnXhD"
    },
    {
        "name": "pokt",
        "url": "https://eth-mainnet.gateway.pokt.network/v1/lb/d518f45b2a8952940ec35399"
    },
    {
        "name": "pokt",
        "url": "https://eth-mainnet.gateway.pokt.network/v1/lb/d518f45b2a8952940ec35399"
    }
    ]

mev_providers = [
    {"name": "flashbots", "url": "https://relay.flashbots.net"},
    {"name": "builder0x69", "url": "http://builder0x69.io"},
    {"name": "edennetwork", "url": "https://api.edennetwork.io/v1/bundle"},
    {"name": "beaverbuild", "url": "https://rpc.beaverbuild.org"},
    {"name": "lightspeedbuilder", "url": "https://rpc.lightspeedbuilder.info"},
    {"name": "eth-builder", "url": "https://eth-builder.com"},
    {"name": "ultrasound", "url": "https://relay.ultrasound.1money"},
    {"name": "agnostic-relay", "url": "https://agnostic-relay.net"},
    {"name": "relayoor-wtf", "url": "https://relayooor.wtf"},
    {"name": "rsync-builder", "url": "https://rsync-builder.xyz"}
]

def send_telegram(text: str, telegram_channel_id, telegram_token):
    try:
        get('https://api.telegram.org/bot{}/sendMessage'.format(telegram_token), params=dict(
        chat_id=telegram_channel_id,
        text=text))
    except:
        print(f'[E] Error send telegram. Reconnect.')
        return False
    else: 
        return True

def send_stat(ip_, from_, to_, value_, tip_):
    url = f'http://{stat_server}/savedata'
    headers = {'Content-Type': 'application/json'}
    data = {'ip_': ip_, 'from_': from_, 'to_': to_ , 'value_': value_, 'tip_': tip_}
    try:
        response = post(url, headers=headers, data=dumps(data))
    except:
        return None
    j = response.json()
    return j['message']

def init_worker():
    signal(SIGINT, SIG_IGN)

def decode_tx(tx):
    original_hexstr = tx
    signed_tx_as_bytes = to_bytes(hexstr=original_hexstr)
    decoded_tx = TransactionBuilder().decode(signed_tx_as_bytes)
    sender = encode_hex(decoded_tx.sender)
    d = decoded_tx.__dict__
    to__ = d['_inner'][5].hex()
    value__ = d['_inner'][6]
    return f"0x{to__.lower()}", value__, sender

def date_str():
    now = datetime.now()
    return now.strftime("%Y/%m/%d/, %H:%M:%S")

def save_file(infile, text):
    if path.exists('log'): pass
    else: mkdir('log')
    file = f'log/{infile}.log'
    f = open(file, 'a', encoding='utf-8', errors='ignore')
    f.write(f'{text}\n')
    f.close()

def send_transaction(data):
    request_data = data[0]
    url = data[1]
    client_ip = data[2]
    tx_to = data[3]
    tx_value = data[4]
    tx_from = data[5]
    
    try:
        response = requests.post(url, headers=headers, data=dumps(request_data))
    except:
        save_file('error', f"{date_str()};IP:{client_ip};TO:{tx_to};FROM:{tx_value};VALUE:{tx_from};response:{response.content}")
    return response.json()

@app.route('/system')
def system():
    cpu_count = psutil.cpu_count()
    return render_template('system.html', cpu_count=cpu_count)

@app.route('/system-data')
def system_data():
    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    memory_percent = psutil.virtual_memory().percent
    cpu_count = psutil.cpu_count()
    return {'cpu_data': cpu_percent, 'memory_data': memory_percent, 'cpu_count': cpu_count}

@app.route('/', methods=['POST'])
def handle_request():
    l = []
    send_client = ''
    client_ip = request.remote_addr
    fast_provider = mainnet_providers[2]['url']
    fast_mev = mev_providers[9]['url']
    num_threads_mev = len(mev_providers)
    num_threads_net = len(mainnet_providers)
    request_data = request.get_json()
    if request_data['method'] == 'eth_sendRawTransaction':
        data = request_data['params']
        raw_transaction = data[0]
        tx_to, tx_value, tx_from = decode_tx(raw_transaction)

        # если найдена транза на мев адрес то делаем подмену    
        if tx_to in mev_addr:
            print('############## MEV ##################')
            #отправка данных на сервер статистики (запускается отдельно)
            try:
                send_stat(client_ip, tx_from, tx_to, str(tx_value), 'MEV')
            except:
                send_telegram(f'[W] Ошибка передачи данных на сервер статистики', telegram_channel_id, telegram_token)
                
            pool = Pool(num_threads_mev, init_worker)
            for num in range(num_threads_mev):
                l.append([request_data, mev_providers[num]['url'], client_ip, tx_to, tx_value, tx_from])
            results = pool.map(send_transaction, l)

            for result in results:
                if 'result' in result:
                    send_client = result
                    save_file('transaction_mev', f"{date_str()};IP:{client_ip};TO:{tx_to};FROM:{tx_value};VALUE:{tx_from};Change provider - yes;send to:{fast_mev}")
                else: 
                    save_file('dump_mev', f"{date_str()};IP:{client_ip};TO:{tx_to};FROM:{tx_value};VALUE:{tx_from};result:{result}")
            
            print('############## MEV ##################')
            if 'result' in send_client:
                return send_client
            else: return None
        
        else:
            print('############## PROVIDERS ##################')
            #отправка данных на сервер статистики (запускается отдельно)
            try:
                send_stat(client_ip, tx_from, tx_to, str(tx_value), 'providers')
            except:
                send_telegram(f'[W] Ошибка передачи данных на сервер статистики', telegram_channel_id, telegram_token)
                
            pool = Pool(num_threads_net, init_worker)
            for num in range(num_threads_net):
                l.append([request_data, mainnet_providers[num]['url'], client_ip, tx_to, tx_value, tx_from])
            results = pool.map(send_transaction, l)

            for result in results:
                if 'result' in result:
                    send_client = result
                    save_file('transaction_provider', f"{date_str()};IP:{client_ip};TO:{tx_to};FROM:{tx_value};VALUE:{tx_from};Change provider - no;send to:{fast_provider}")
                else:
                    save_file('dump_provider', f"{date_str()};IP:{client_ip};TO:{tx_to};FROM:{tx_value};VALUE:{tx_from};result:{result}")
            
            print('############## PROVIDERS ##################')
            if 'result' in send_client:
                return send_client
            else: return None
    else:
        response = requests.post(fast_provider, headers=headers, data=dumps(request_data))
        save_file('response',f'{response.content}')
        return response.content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3100)
