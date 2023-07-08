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

version = 'proxy server 0.10 / 08.07.23'
telegram_token = '5311024399:AAF6Ov-sMSc4dd2DDdx0hF_B-5-4vPerFTs'
telegram_channel_id = '@scanpvknon'
app = Flask(__name__)

stat_server = '127.0.0.1:3200'
proxy_port = 3100
mode = ''

testnet_providers = [
    {
        "name": "Infura",
        "url": "https://goerli.infura.io/v3/4766aaf656954c52ae92eed6abc7f8cc"
    },
    {
        "name": "test",
        "url": "https://goerli.blockpi.network/v1/rpc/public"
    },
    {
        "name": "test2",
        "url": "https://eth-goerli.public.blastapi.io"
    }
    ]

testnet_providers_ = [
    {
        "name": "Infura",
        "url": "https://goerli.infura.io/v3/4766aaf656954c52ae92eed6abc7f8cc"
    },
    {
        "name": "test",
        "url": "https://goerli.blockpi.network/v1/rpc/public"
    },
    {
        "name": "test2",
        "url": "https://eth-goerli.public.blastapi.io"
    },
    {
        "name": "test3",
        "url": "https://goerli.gateway.tenderly.co"
    }
    ]

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
        "url": "https://eth-mainnet.g.alchemy.com/v2/ANUgbxXb5fRwPxLlAZ9fGcKGYdcoaik5"
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

fast_mainnet_provider = ""
fast_mev_provider = ""
mev_addr = ['0x7a250d5630b4cf539739df2c5dacb4c659f2488d','0xef1c6e67703c7bd7107eed8303fbe6ec2554bf6b','0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad']
headers = {'Content-Type': 'application/json'}

def init_worker():
    signal(SIGINT, SIG_IGN)

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

def send_stat(ip_, from_, to_, value_):
    url = f'http://{stat_server}/savedata'
    headers = {'Content-Type': 'application/json'}
    data = {'ip_': ip_, 'from_': from_, 'to_': to_ , 'value_': value_}
    try:
        response = post(url, headers=headers, data=dumps(data))
    except:
        return None
    j = response.json()
    return j['message']

def decode_tx(tx):
    original_hexstr = tx
    signed_tx_as_bytes = to_bytes(hexstr=original_hexstr)
    decoded_tx = TransactionBuilder().decode(signed_tx_as_bytes)
    sender = encode_hex(decoded_tx.sender)
    d = decoded_tx.__dict__
    return d['_inner'][5].hex(), d['_inner'][6], sender

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

def find_key(prov_list, value):
    for dictionary in prov_list:
        for key, val in dictionary.items():
            if val == value:
                return dictionary['url']
    return None

def check_provider_speed(provider):
    try:
        start_time = time()
        response = requests.get(provider["url"])
        end_time = time()
        response_time = end_time - start_time
        return response_time
    except requests.exceptions.RequestException as e:
        return None
    
def sort_provide(prov_list):
    response_times = {}
    for provider in prov_list:
        response_time = check_provider_speed(provider)
        if response_time is not None:
            response_times[provider["name"]] = response_time
    fastest_provider = min(response_times, key=response_times.get)
    return fastest_provider

def send_transaction(data):
    request_data = data[0]
    url = data[1]
    response = requests.post(url, headers=headers, data=dumps(request_data))
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
    global fast_provider
    global fast_mev
    global num_threads_mev
    global num_threads_net
    global mode
    request_data = request.get_json()
    if request_data['method'] == 'eth_sendRawTransaction':
        data = request_data['params']
        raw_transaction = data[0]
        tx_to, tx_value, tx_from = decode_tx(raw_transaction)
        #отправка данных на сервер статистики (запускается отдельно)
        try:
            send_stat(client_ip, tx_from, tx_to, str(tx_value))
        except:
            send_telegram(f'[W] Ошибка передачи данных на сервер статистики', telegram_channel_id, telegram_token)
        # если найдена транза на мев адрес то делаем подмену    
        if tx_to in mev_addr:
            print('############## MEV ##################')
            pool = Pool(num_threads_mev, init_worker)
            for num in range(num_threads_mev):
                l.append([request_data, mev_providers[num]['url']])
            results = pool.map(send_transaction, l)

            for result in results:
                print(f'------------- -------- {result} ---- --------------')
                if 'result' in result:
                    send_client = result
                    save_file('transaction_provider', f"{date_str()};IP:{client_ip};TO:{tx_to};FROM:{tx_value};VALUE:{tx_from};Change provider - yes;send to:{fast_mev}")
                else: print(f'Result ------------> {result}')
            
            print('############## MEV ##################')
            if 'result' in send_client:
                return send_client
            else: return None
        
        else:
            #если тестовый запуск берем данные из словаря тестового
            if mode == 'test':
                print('############## PROVIDERS ##################')
                pool = Pool(num_threads_net, init_worker)
                for num in range(num_threads_net):
                    l.append([request_data, testnet_providers[num]['url']])
                results = pool.map(send_transaction, l)

                for result in results:
                    print(f'------------- -------- {result} ---- --------------')
                    if 'result' in result:
                        send_client = result
                        save_file('transaction_provider', f"{date_str()};IP:{client_ip};TO:{tx_to};FROM:{tx_value};VALUE:{tx_from};Change provider - no;send to:{fast_provider}")
                    else: print(f'Result ------------> {result}')
                
                print('############## PROVIDERS ##################')
                if 'result' in send_client:
                    return send_client
                else: return None
            else:
                print('############## PROVIDERS ##################')
                pool = Pool(num_threads_net, init_worker)
                for num in range(num_threads_net):
                    l.append([request_data, mainnet_providers[num]['url']])
                results = pool.map(send_transaction, l)

                for result in results:
                    print(f'------------- -------- {result} ---- --------------')
                    if 'result' in result:
                        send_client = result
                        save_file('transaction_provider', f"{date_str()};IP:{client_ip};TO:{tx_to};FROM:{tx_value};VALUE:{tx_from};Change provider - no;send to:{fast_provider}")
                    else: print(f'Result ------------> {result}')
                
                print('############## PROVIDERS ##################')
                if 'result' in send_client:
                    return send_client
                else: return None
    else:
        response = requests.post(fast_provider, headers=headers, data=dumps(request_data))
        save_file('response',f'{response}')
        return response.content

if __name__ == '__main__':
    freeze_support()
    net = 'mainnet' #argv[1]
    mode = net
    print(f'[I] Version: {version}')
    print(f'[I] Stat server: {stat_server}')
    print('[*] Starting checks provider ...')
    
    if net != 'test':
        print('[I] Запущена основная сеть')
        res = sort_provide(mainnet_providers)
        fast_provider = 'https://eth-mainnet.g.alchemy.com/v2/ANUgbxXb5fRwPxLlAZ9fGcKGYdcoaik5'#find_key(mainnet_providers, res)
        num_threads_net = len(mainnet_providers)
    else:
        #======= test =======
        print(f'[I] Запущена тестовая сеть')
        res = sort_provide(testnet_providers)
        fast_provider = find_key(testnet_providers, res)
        num_threads_net = len(testnet_providers)
        #====================
        
    res = sort_provide(mev_providers)
    fast_mev = find_key(mev_providers, res)
    num_threads_mev = len(mev_providers)

    
    print(f'[I] Best server provider: {fast_provider}')
    print(f'[I] Best server MEV: {fast_mev}')
    app.run(host='0.0.0.0', port=proxy_port)
