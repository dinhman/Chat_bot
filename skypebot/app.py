from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import subprocess
import os
import signal

app = Flask(__name__)
app.config['SECRET_KEY'] = '6JMdyv3ArPvBbQkX'
socketio = SocketIO(app)

process = None
terminal_output = []

@app.route('/')
def index():
    return render_template('index.html', terminal_output=terminal_output)

@socketio.on('start_process')
def start_process():
    global process
    if process is None or process.poll() is not None:
        process = subprocess.Popen(['python', 'main3.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        socketio.start_background_task(target=background_process_output)
        emit('process_status', 'Process started.')
    else:
        emit('process_status', 'Process is already running.')

@socketio.on('stop_process')
def stop_process():
    global process
    if process and process.poll() is None:
        os.kill(process.pid, signal.SIGTERM)
        process = None
        emit('process_status', 'Process stopped.')
    else:
        emit('process_status', 'No running process to stop.')

@socketio.on('restart_process')
def restart_process():
    stop_process()
    start_process()

def background_process_output():
    global process, terminal_output
    while process.poll() is None:
        line = process.stdout.readline()
        if line:
            terminal_output.append(line.strip())
            socketio.emit('terminal_output', line.strip())
    process = None

if __name__ == '__main__':
    socketio.run(app)
