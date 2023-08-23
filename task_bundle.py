#!/usr/bin/python3
# encoding=utf-8
# -*- coding: utf-8 -*-
"""
@author: NonameHUNT
@GitHub: https://github.com/Noname400
@telegram: https://t.me/NonameHunt
"""

from function_lib_bundle import *

version = 'task pool bundle 1.15 / 20.08.23'

def process_json(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'message' and (value in msg): return True
            if key == 'result' and value != None: return True
            if process_json(value): return True
    elif isinstance(data, list):
        for item in data:
            process_json(item)
    else:
        pass
    return False

def send_transaction(task):
    save_file(f'control_task', f'{date_str()};{task}')
    url_mev:str = task[0]
    request = task[1]
    data = task[2]
    desc:str = task[3]
    
    if desc == 'mev':
        res = send_bundle_proxy(url_mev, data["url_provider"], request['params'][0][2:], data['to'])
        return res

    # elif desc == "mev_":
    #     headers = data["header"]
    #     print(f'DATA URL: {url} | {headers}')
    #     bundle_dict = {"jsonrpc": request["jsonrpc"], "id": request["id"], "method": "eth_sendBundle", "params": [{"txs": {request["params"]}, "blockNumber": block}]}
    #     bundle_dict['params'][0]['txs'].append(request["params"][0])
    #     response = post(url, headers=headers, data=dumps(bundle_dict))
    #     if response.status_code == 200:
    #         if process_json(response.json()):
    #             save_file(f'done-task-send-{desc}', f'{date_str()};{url};{task};{bundle_dict}')
    #             save_stat(data["ip"], data["from"], data["to"], str(data["value"]), desc)
    #             return True, task
    #     else:
    #         save_file(f'error-task-status_code-{desc}', f'{date_str()};{url};{request};{data};{bundle_dict}')
    #         return False, task

    return None

def process_tasks():
    print(f'Start {version}')
    # while True:
    #     task = redis_client.lpop('task_queue')
    #     if task is not None:
    #         task = task.decode('utf-8')
    #         task_data = loads(task)
    #         print(f'Задание получил : {task_data}')
    #         save_file('get_task', task_data)
    #         send_transaction(task_data)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        while True:
            task = redis_client.lpop('task_queue')
            if task is not None:
                task = task.decode('utf-8')
                task_data = loads(task)
                print(f'Задание получил : {task_data}')
                save_file('get_task', task_data)
                executor.submit(send_transaction, task_data)

if __name__ == '__main__':
    process_tasks()