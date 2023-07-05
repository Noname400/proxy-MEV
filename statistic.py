#!/usr/bin/python3
# encoding=utf-8
# -*- coding: utf-8 -*-

"""
@author: NonameHUNT
@GitHub: https://github.com/Noname400
@telegram: https://t.me/NonameHunt
"""

version = 'server statistic 0.1 rev/05.07.23'
telegram_token = '5311024399:AAF6Ov-sMSc4dd2DDdx0hF_B-5-4vPerFTs'
telegram_channel_id = '@scanpvknon'

from flask import Flask, request, jsonify, render_template
from datetime import datetime
import sqlite3
from os import path, mkdir, system, name
from sys import argv

app = Flask(__name__)
app.secret_key = 'cba0a242e99c1c6dce337df4757ab7803b93f38003a9b5de1f945ca4ca716c08'

def save_file(infile, desc, text):
    if path.exists('log'): pass
    else: mkdir('log')
    file = f'log/{infile}-{desc}.log'
    f = open(file, 'a', encoding='utf-8', errors='ignore')
    f.write(f'[*] {text}\n')
    f.close()

def date_str():
    now = datetime.now()
    return now.strftime("%Y/%m/%d/, %H:%M:%S")

@app.route('/savedata', methods=['POST'])
def savedata():
    counts = 0
    name = request.json['name']
    mnemonic = request.json['mnemonic']
    begin = request.json['begin']
    end = request.json['end']
    path = request.json['path']
    coin = request.json['coin']
    msg = request.json['msg']
    pvk = request.json['pvk']
    mode = request.json['mode']

    conn_old = sqlite3.connect(DB_OLD)
    select_query_old = "SELECT mnemonic, coin FROM found WHERE mnemonic = ? AND coin = ?"
    existing_row_old = conn_old.execute(select_query_old, (mnemonic, coin,)).fetchone()
    print(existing_row_old)

    conn = sqlite3.connect(DB)
    select_query = "SELECT counts FROM found WHERE mnemonic = ? AND coin = ?"
    existing_row = conn.execute(select_query, (mnemonic, coin,)).fetchone()
    print(existing_row_old, existing_row)

    if existing_row_old != None:
        counts = 1
        insert_query = "INSERT INTO foundold (name, mnemonic, counts, begin, end, path, coin, msg, pvk, mode, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        conn.execute(insert_query, (name, mnemonic, counts, begin, end, path, coin, msg, pvk, mode, date_str()))
        conn.commit()
        conn.close()
        conn_old.close()
        return jsonify({'message': 'Data dabbling'})

    # if existing_row_old != None and existing_row != None:
    #     print('Запись в новой и старой базе найдены .........')
    #     counts = existing_row[0]
    #     counts += 1
    #     update_query = "UPDATE found SET counts = ? WHERE mnemonic = ? AND coin = ?"
    #     conn.execute(update_query, (counts, mnemonic, coin,))

    if existing_row != None:
        print('Запись в новой базе найдена а в старой нет .........')
        counts = existing_row[0]
        counts += 1
        update_query = "UPDATE found SET counts = ? WHERE mnemonic = ? AND coin = ?"
        conn.execute(update_query, (counts, mnemonic, coin,))
        conn.commit()
        conn.close()
        conn_old.close()
        return jsonify({'message': 'Data UPDATE'})

    else:
        counts = 1
        insert_query = "INSERT INTO found (name, mnemonic, counts, begin, end, path, coin, msg, pvk, mode, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        conn.execute(insert_query, (name, mnemonic, counts, begin, end, path, coin, msg, pvk, mode, date_str()))
        conn.commit()
        conn.close()
        conn_old.close()
        return jsonify({'message': 'Data saved successfully'})

@app.route('/stat')
def stat():
    limit = request.args.get('limit', default=100, type=int)
    page = request.args.get('page', default=1, type=int)
    offset = (page - 1) * limit
    conn = sqlite3.connect(DB)
    cursor = conn.execute(f'SELECT * FROM numbers LIMIT {limit} OFFSET {offset}')
    data = cursor.fetchall()
    len_ = len(data)
    conn.close()
    return render_template('stat.html', data=data, limit=limit, page=page, len_=len_)

if __name__ == '__main__':
    DB = f'database_v1.db'
    NUMBER = 0
    print('-'*70,end='\n')
    print(f'[I] Version: {version}')
    print(f'[I] Start proogramm: {date_str()}')
    print(f'[I] File DB: {DB}')
    print('-'*70,end='\n')

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS numbers (id INTEGER PRIMARY KEY, number INTEGER, name TEXT, range_start INTEGER, range_end INTEGER, ver TEXT, timestamp TEXT)')
    conn.commit()
    conn.close()
    
    app.run(host='0.0.0.0', port=3200)
