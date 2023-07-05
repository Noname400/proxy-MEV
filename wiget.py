from flask import Flask, render_template
import psutil

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)
