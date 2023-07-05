#!/usr/bin/python3
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

app = Flask(__name__)
app.secret_key = 'cba0a242e99c1c6dce337df4757ab7803b93f38003a9b5de1f945ca4ca716c08'

def save_file(infile, desc, text):
    if path.exists('log'): pass
    else: mkdir('log')
    filename = f'log/{infile}-{desc}.log'
    f = open(filename, encoding='utf-8', errors='ignore', mode='a')
    f.write(f'[*] {text}\n')
    f.close()

def date_str():
    now = datetime.now()
    return now.strftime("%Y/%m/%d/ %H:%M:%S")

@app.route('/savedata', methods=['POST'])
def savedata():
    counts = 0
    print(request.json)
    ip_ = request.json['ip_']
    from_ = request.json['from_']
    to_ = request.json['to_']
    value_ = request.json['value_']
    print(request.json)

    conn = sqlite3.connect(DB)
    select_query = "SELECT count_ FROM stat WHERE from_ = ? AND to_ = ?"
    existing_row_from_to = conn.execute(select_query, (from_, to_)).fetchone()
    
    if existing_row_from_to is not None:
        counts = existing_row_from_to[0] + 1
        update_query = "UPDATE stat SET from_ = ?, to_ = ?, value_ = ?, count_ = ?, timestamp_ = ?  WHERE from_ = ? AND to_ = ?"
        conn.execute(update_query, (from_, to_, value_, counts, date_str(), from_, to_))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Data +'})

    else:
        insert_query = "INSERT INTO stat (ip_, from_, to_, value_, count_, timestamp_) VALUES (?, ?, ?, ?, ?, ?)"
        conn.execute(insert_query, (ip_, from_, to_, value_, 1, date_str()))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Data add'})

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
    c.execute('CREATE TABLE IF NOT EXISTS stat (id INTEGER PRIMARY KEY, ip_ TEXT, from_ TEXT, to_ TEXT, value_ TEXT, count_ INTEGER, timestamp_ TEXT)')
    conn.commit()
    conn.close()
    
    app.run(host='0.0.0.0', port=3200)
