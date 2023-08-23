#!/usr/bin/python3
# encoding=utf-8
# -*- coding: utf-8 -*-
"""
@author: NonameHUNT
@GitHub: https://github.com/Noname400
@telegram: https://t.me/NonameHunt
"""
from function_lib_bundle import *

version = 'proxy server bundle 2.14 / 20.08.23'

app = Flask(__name__)
create_db(DB)

@app.route('/', methods=['POST'])
def handle_request():
    try:
        request_data = request.get_json()
    except:
        save_file('error_request_data', f'{date_str()};{request_data}')
        res = {'jsonrpc': '2.0', 'id': 1, 'result': 'error request data'}
        return dumps(res)
    
    DATA = data()
    DATA.ip_ = request.environ['REMOTE_ADDR'] #request.remote_addr
    if request_data["method"] == 'eth_sendRawTransaction':
        print('------------- request_data eth_sendRawTransaction --------------------------------')
        fill_class(DATA, request_data)
        DATA.request = request_data
        DATA.create_hash_tx()
        DATA.decode_tx_raw()
        save_file('request_data_eth_sendRawTransaction', f'{date_str()};{request_data}')   
        #if search_allow('allow_users', f'{DATA.from_}') and DATA.to_.lower() in scan_addr:
        if searsh_list(DATA.to_, scan_addr):
            ################## MEV ##################
            for num in range(DATA.num_threads_mev):
                redis_client.rpush('task_queue',  dumps([mev_providers[num]['url'], request_data, DATA.dict_redis(), 'mev'])) #
                save_file(f'task_queue_mev', f'{date_str()};{mev_providers[num]["url"]};{request_data};{DATA.dict_redis()};"mev"') #
            res = DATA.dict_hash_tx()
            return dumps(res)
            ################## MEV ##################
        else:
            ################## PROVIDERS ##################
            save_file('auth_tx_reject', f'{date_str()};{request_data};{DATA.__dict__}')
            save_file(f'task_queue_provider', f'{date_str()};{request_data};{DATA.dict_redis()};"provider"')
            response = post(DATA.mainnet_providers, headers=DATA.headers, data=dumps(request_data))
            return response.content
            ################## PROVIDERS ##################
    # elif request_data["method"] == 'eth_sendBundle':
    #     fill_class(DATA, request_data)
    #     DATA.create_hash_tx_bundle()
    #     DATA.decode_tx_bundle()
    #     DATA.params = DATA.params[0]['txs']
    #     # у бандлов params по другому заполняется, смотри внимательно. его надо отдельно заполнить ы ручную
    #     save_file('request_data_eth_bundle', f'{date_str()};{request_data}')   
    #     if search_allow('allow_tx', f'{DATA.from_}'):
    #         ################## BUNDLE ##################
    #         for num in range(DATA.num_threads_mev):
    #             redis_client.rpush('task_queue',  dumps([mev_providers[num]['url'],  request_data, DATA.dict_redis(), 0, 'bundle']))
    #             save_file('task_queue_bundle', f'{date_str()};{mev_providers[num]["url"]};{request_data};{DATA.dict_redis()};"bundle"')
    #         res = DATA.dict_bundle()
    #         return dumps(res)
    #     ################## BUNDLE ##################
    else:
        response = post(DATA.mainnet_providers, headers=DATA.headers, data=dumps(request_data))
        return response.content

@app.route('/stat')
def stat():
    limit = request.args.get('limit', default=50, type=int)
    page = request.args.get('page', default=1, type=int)
    offset = (page - 1) * limit
    conn = sqlite3.connect(DB)
    cursor = conn.execute(f'SELECT * FROM stat LIMIT {limit} OFFSET {offset}')
    data = cursor.fetchall()
    len_ = len(data)
    conn.close()
    return render_template('stat.html', data=data, limit=limit, page=page, len_=len_)

@app.route('/allow', methods=['GET', 'POST'])
def allow():
    if request.method == 'POST':
        addr = request.form['addr']
        if addr:
            conn = get_db_connection()
            conn.execute('INSERT INTO allow_users (addr) VALUES (?)', (addr,))
            conn.commit()
            conn.close()

    conn = get_db_connection()
    data = conn.execute('SELECT * FROM allow_users').fetchall()
    conn.close()
    return render_template('allow.html', data=data)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_entry(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM allow_users WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('allow'))

@app.route('/add', methods=['POST'])
def add_entry():
    addr = request.form['addr']
    if addr:
        conn = get_db_connection()
        existing_entry = conn.execute('SELECT * FROM allow_users WHERE addr = ?', (addr,)).fetchone()

        if existing_entry:
            message = f"Запись с адресом '{addr}' уже существует."
        else:
            conn.execute('INSERT INTO allow_users (addr) VALUES (?)', (addr,))
            conn.commit()
            message = f"Запись с адресом '{addr}' успешно добавлена."
        conn.close()
    else:
        message = "Адрес не может быть пустым."
    return redirect(url_for('allow', message=message))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3200)
