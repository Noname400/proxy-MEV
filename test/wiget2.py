from flask import Flask, render_template, jsonify
import psutil

app = Flask(__name__)

def get_cpu_load():
    return psutil.cpu_percent(interval=1)

@app.route('/')
def index():
    return render_template('system2.html')

@app.route('/cpu_load')
def cpu_load():
    cpu_load = get_cpu_load()
    return jsonify(cpu_load=cpu_load)

if __name__ == '__main__':
    app.run(debug=True)
