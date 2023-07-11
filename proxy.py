#!/usr/bin/python3
# encoding=utf-8
# -*- coding: utf-8 -*-
"""
@author: NonameHUNT
@GitHub: https://github.com/Noname400
@telegram: https://t.me/NonameHunt
"""

from function_lib import *

version = 'proxy server 0.19 mainnet / 11.07.23'

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'  # URL для Redis
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'  # URL для Redis
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

fast_mainnet_provider = ""
fast_mev_provider = ""
scan_addr = ['0x7a250d5630b4cf539739df2c5dacb4c659f2488d','0xef1c6e67703c7bd7107eed8303fbe6ec2554bf6b','0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad']

@celery.task
def send_transaction(*args):
    for i in range(len(args)):
        request_data = args[i][0]
        url = args[i][1]
        client_ip = args[i][2]
        tx_to = args[i][3]
        tx_value = args[i][4]
        tx_from = args[i][5]
        desc = args[i][6]
        try:
            response = requests.post(url, headers=headers, data=dumps(request_data))
        except:
            save_file(f'error-{desc}', f"{date_str()};IP:{client_ip};TO:{tx_to};FROM:{tx_value};VALUE:{tx_from};response:{response.content};result:{response.json()}")
        
        if 'result' in response.json():
            save_file(f'transaction_provider-{desc}', f"{date_str()};IP:{client_ip};TO:{tx_to};FROM:{tx_from};VALUE:{tx_value};SEND:{url};result:{response.json()}")
        else:
            save_file(f'dump_provider-{desc}', f"{date_str()};IP:{client_ip};TO:{tx_to};FROM:{tx_from};VALUE:{tx_value};result:{response.json()}")

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
    client_ip = request.remote_addr
    fast_provider = mainnet_providers[2]['url']
    num_threads_mev = len(mev_providers)
    num_threads_net = len(mainnet_providers)
    request_data = request.get_json()
    
    if request_data['method'] == 'eth_sendRawTransaction':
        save_file('request_data', request_data)
        raw_tx.id = request_data['id']
        raw_tx.raw = request_data['params'][0]
        raw_tx.hash_tx = f'0x{keccak(bytes.fromhex(raw_tx.raw[2:])).hex()}'        
        tx_to, tx_value, tx_from = decode_tx(raw_tx.raw)
        # если найдена транза на scan_addr
        if tx_to in scan_addr:
            ############## MEV ##################
            #отправка данных на сервер статистики (запускается отдельно)
            try:
                send_stat(client_ip, tx_from, tx_to, str(tx_value), 'mev')
            except:
                send_telegram(f'[W] Ошибка передачи данных на сервер статистики', telegram_channel_id, telegram_token)
            
            for num in range(num_threads_mev):
                l.append([request_data, mev_providers[num]['url'], client_ip, tx_to, tx_value, tx_from, 'mev'])
                
            task = send_transaction.apply_async(args=l, ignore_result=True)
            res = {'jsonrpc': '2.0', 'id': raw_tx.id, 'result': raw_tx.hash_tx}
            return dumps(res)
            ############## MEV ##################
        else:
            ############## PROVIDERS ##################'
            #отправка данных на сервер статистики (запускается отдельно)
            try:
                send_stat(client_ip, tx_from, tx_to, str(tx_value), 'providers')
            except:
                send_telegram(f'[W] Ошибка передачи данных на сервер статистики', telegram_channel_id, telegram_token)
            
            for num in range(num_threads_net):
                l.append([request_data, mainnet_providers[num]['url'], client_ip, tx_to, tx_value, tx_from, 'provider'])
                
            task = send_transaction.apply_async(args=l, ignore_result=True)
            res = {'jsonrpc': '2.0', 'id': raw_tx.id, 'result': raw_tx.hash_tx}
            return dumps(res)
            ############## PROVIDERS ##################'
    else:
        response = requests.post(fast_provider, headers=headers, data=dumps(request_data))
        return response.content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3100)
