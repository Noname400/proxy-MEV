#!/usr/bin/python3
# encoding=utf-8
# -*- coding: utf-8 -*-
"""
@author: NonameHUNT
@GitHub: https://github.com/Noname400
@telegram: https://t.me/NonameHunt
"""

from function_lib import *

version = 'proxy server 0.15 mainnet / 10.07.23'

app = Flask(__name__)

fast_mainnet_provider = ""
fast_mev_provider = ""
scan_addr = ['0x7a250d5630b4cf539739df2c5dacb4c659f2488d','0xef1c6e67703c7bd7107eed8303fbe6ec2554bf6b','0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad']

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

        # если найдена транза на scan_addr
        if tx_to in scan_addr:
            print('############## MEV ##################')
            #отправка данных на сервер статистики (запускается отдельно)
            try:
                send_stat(client_ip, tx_from, tx_to, str(tx_value), 'MEV')
            except:
                send_telegram(f'[W] Ошибка передачи данных на сервер статистики', telegram_channel_id, telegram_token)
                
            pool = Pool(num_threads_mev, init_worker)
            for num in range(num_threads_mev):
                l.append([request_data, mev_providers[num]['url'], client_ip, tx_to, tx_value, tx_from, 'mev'])
            results = pool.map(send_transaction, l)

            for result in results:
                if result == None: continue
                if 'result' in result:
                    send_client = result
                    save_file('transaction_mev', f"{date_str()};IP:{client_ip};TO:{tx_to};FROM:{tx_value};VALUE:{tx_from};SEND:{fast_mev}")
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
                l.append([request_data, mainnet_providers[num]['url'], client_ip, tx_to, tx_value, tx_from, 'provider'])
            results = pool.map(send_transaction, l)

            for result in results:
                if result == None: continue
                if 'result' in result:
                    send_client = result
                    save_file('transaction_provider', f"{date_str()};IP:{client_ip};TO:{tx_to};FROM:{tx_value};VALUE:{tx_from};SEND:{fast_provider}")
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
